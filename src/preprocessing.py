"""
Data Preprocessing Module

This module handles data ingestion, cleaning, and preprocessing operations.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.logger import get_logger
from backend.utils import load_config, ensure_directory


class DataPreprocessor:
    """
    Data preprocessing class for HHS UAC Program data.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the DataPreprocessor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or load_config()
        self.logger = get_logger(__name__)
        self.df: Optional[pd.DataFrame] = None
        
    def load_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load CSV data file.
        
        Args:
            file_path: Path to CSV file (optional, uses config if not provided)
            
        Returns:
            Loaded DataFrame
        """
        if file_path is None:
            file_path = self.config["data"]["raw_path"]
        
        self.logger.info(f"Loading data from: {file_path}")
        
        try:
            self.df = pd.read_csv(file_path, encoding='utf-8')
            self.logger.info(f"Successfully loaded {len(self.df)} rows")
            
            # Drop completely empty rows
            original_length = len(self.df)
            self.df = self.df.dropna(how='all')
            dropped_rows = original_length - len(self.df)
            if dropped_rows > 0:
                self.logger.info(f"Dropped {dropped_rows} completely empty rows")
            
            return self.df
        except UnicodeDecodeError:
            # Try with different encoding
            self.df = pd.read_csv(file_path, encoding='latin1')
            self.logger.info(f"Successfully loaded {len(self.df)} rows with latin1 encoding")
            
            # Drop completely empty rows
            original_length = len(self.df)
            self.df = self.df.dropna(how='all')
            dropped_rows = original_length - len(self.df)
            if dropped_rows > 0:
                self.logger.info(f"Dropped {dropped_rows} completely empty rows")
            
            return self.df
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise
    
    def clean_numeric_columns(self) -> pd.DataFrame:
        """
        Clean numeric columns by removing commas and converting to numeric.
        
        Returns:
            DataFrame with cleaned numeric columns
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Cleaning numeric columns (removing commas, etc.)")
        
        # Get all columns except date column
        date_col = self.config["data"]["date_column"]
        columns_to_clean = [col for col in self.df.columns if col != date_col]
        
        for col in columns_to_clean:
            if self.df[col].dtype == 'object':
                # Remove commas and convert to numeric
                self.df[col] = self.df[col].astype(str).str.replace(',', '', regex=False)
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            elif self.df[col].dtype != 'object':
                # Already numeric, just ensure it's clean
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        self.logger.info("Numeric columns cleaned successfully")
        
        return self.df
    
    def rename_columns(self) -> pd.DataFrame:
        """
        Rename columns to match expected naming convention.
        
        Returns:
            DataFrame with renamed columns
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Renaming columns to match expected format")
        
        # Define column mapping based on new CSV structure
        column_mapping = {
            "Children apprehended and placed in CBP custody*": "CBP_Apprehended",
            "Children in CBP custody": "CBP_Custody",
            "Children transferred out of CBP custody": "Transfers",
            "Children in HHS Care": "HHS_Care",
            "Children discharged from HHS Care": "Discharges"
        }
        
        # Only rename columns that exist in the dataframe
        existing_mapping = {k: v for k, v in column_mapping.items() if k in self.df.columns}
        
        if existing_mapping:
            self.df = self.df.rename(columns=existing_mapping)
            self.logger.info(f"Renamed columns: {list(existing_mapping.keys())}")
        else:
            self.logger.info("No columns needed renaming - already using expected format")
        
        return self.df
    
    def convert_date_column(self, date_column: Optional[str] = None) -> pd.DataFrame:
        """
        Convert date column to datetime format.
        
        Args:
            date_column: Name of date column (optional, uses config if not provided)
            
        Returns:
            DataFrame with converted date column
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        date_col = date_column or self.config["data"]["date_column"]
        
        if date_col not in self.df.columns:
            raise ValueError(f"Date column '{date_col}' not found in data")
        
        self.logger.info(f"Converting date column: {date_col}")
        
        date_format = self.config["preprocessing"]["date_format"]
        
        try:
            # Try primary format first
            self.df[date_col] = pd.to_datetime(
                self.df[date_col],
                format=date_format,
                errors='coerce'
            )
            
            # Check for failed conversions and try alternative formats
            failed_conversions = self.df[date_col].isna().sum()
            if failed_conversions > 0:
                self.logger.warning(f"Failed to convert {failed_conversions} dates with primary format, trying alternatives")
                
                # Try alternative formats
                alternative_formats = [
                    "%B %d, %Y",  # December 21, 2025
                    "%m/%d/%Y",   # 12/21/2025
                    "%Y-%m-%d",   # 2025-12-21
                    "%d-%b-%Y",   # 21-Dec-2025
                ]
                
                for alt_format in alternative_formats:
                    mask = self.df[date_col].isna()
                    if mask.sum() > 0:
                        self.df.loc[mask, date_col] = pd.to_datetime(
                            self.df.loc[mask, date_col],
                            format=alt_format,
                            errors='coerce'
                        )
                
                # Final attempt with pandas date parsing
                still_failed = self.df[date_col].isna().sum()
                if still_failed > 0:
                    self.logger.warning(f"Still failed to convert {still_failed} dates, trying pandas flexible parsing")
                    mask = self.df[date_col].isna()
                    if mask.sum() > 0:
                        self.df.loc[mask, date_col] = pd.to_datetime(
                            self.df.loc[mask, date_col],
                            errors='coerce'
                        )
            
            # Check final failed conversions
            final_failed = self.df[date_col].isna().sum()
            if final_failed > 0:
                self.logger.warning(f"Failed to convert {final_failed} dates even with alternative formats")
            
            self.logger.info("Date conversion completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error converting dates: {str(e)}")
            raise
        
        return self.df
    
    def sort_chronologically(self, date_column: Optional[str] = None) -> pd.DataFrame:
        """
        Sort DataFrame chronologically by date column.
        
        Args:
            date_column: Name of date column (optional, uses config if not provided)
            
        Returns:
            Sorted DataFrame
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        date_col = date_column or self.config["data"]["date_column"]
        
        ascending = self.config["preprocessing"]["sort_ascending"]
        
        self.logger.info(f"Sorting data by {date_col} (ascending={ascending})")
        
        self.df = self.df.sort_values(by=date_col, ascending=ascending)
        
        return self.df
    
    def reset_index(self) -> pd.DataFrame:
        """
        Reset DataFrame index.
        
        Returns:
            DataFrame with reset index
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if self.config["preprocessing"]["reset_index"]:
            self.logger.info("Resetting DataFrame index")
            self.df = self.df.reset_index(drop=True)
        
        return self.df
    
    def create_continuous_timeline(self, date_column: Optional[str] = None) -> pd.DataFrame:
        """
        Create continuous daily timeline by filling missing dates.
        
        Args:
            date_column: Name of date column (optional, uses config if not provided)
            
        Returns:
            DataFrame with continuous timeline
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if not self.config["preprocessing"]["fill_missing_dates"]:
            return self.df
        
        date_col = date_column or self.config["data"]["date_column"]
        
        self.logger.info("Creating continuous daily timeline")
        
        # Get date range
        min_date = self.df[date_col].min()
        max_date = self.df[date_col].max()
        
        # Create complete date range
        all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
        
        # Create DataFrame with all dates
        df_complete = pd.DataFrame({date_col: all_dates})
        
        # Merge with existing data
        original_length = len(self.df)
        self.df = df_complete.merge(self.df, on=date_col, how='left')
        
        added_rows = len(self.df) - original_length
        self.logger.info(f"Added {added_rows} missing dates to timeline")
        
        return self.df
    
    def remove_duplicates(self, date_column: Optional[str] = None) -> pd.DataFrame:
        """
        Remove duplicate rows based on date column.
        
        Args:
            date_column: Name of date column (optional, uses config if not provided)
            
        Returns:
            DataFrame with duplicates removed
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if not self.config["preprocessing"]["remove_duplicates"]:
            return self.df
        
        date_col = date_column or self.config["data"]["date_column"]
        
        original_length = len(self.df)
        duplicates = self.df.duplicated(subset=[date_col]).sum()
        
        if duplicates > 0:
            self.logger.info(f"Removing {duplicates} duplicate rows")
            self.df = self.df.drop_duplicates(subset=[date_col], keep='first')
        else:
            self.logger.info("No duplicate rows found")
        
        return self.df
    
    def forward_fill_numeric(self) -> pd.DataFrame:
        """
        Forward fill missing numeric values.
        
        Returns:
            DataFrame with filled values
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Forward filling missing numeric values")
        
        # Get numeric columns (excluding date column)
        date_col = self.config["data"]["date_column"]
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Forward fill
        self.df[numeric_cols] = self.df[numeric_cols].ffill()
        
        # Backward fill any remaining NaNs at the beginning
        self.df[numeric_cols] = self.df[numeric_cols].bfill()
        
        # Fill any remaining NaNs with 0
        self.df[numeric_cols] = self.df[numeric_cols].fillna(0)
        
        return self.df
    
    def save_processed_data(self, output_path: Optional[str] = None) -> str:
        """
        Save processed data to CSV.
        
        Args:
            output_path: Output file path (optional, uses config if not provided)
            
        Returns:
            Path to saved file
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if output_path is None:
            output_path = self.config["data"]["processed_path"]
        
        # Ensure output directory exists
        output_file = Path(output_path)
        ensure_directory(str(output_file.parent))
        
        self.logger.info(f"Saving processed data to: {output_path}")
        
        self.df.to_csv(output_path, index=False, encoding='utf-8')
        
        self.logger.info(f"Successfully saved {len(self.df)} rows")
        
        return output_path
    
    def preprocess_pipeline(self, input_path: Optional[str] = None, 
                           output_path: Optional[str] = None) -> pd.DataFrame:
        """
        Run complete preprocessing pipeline.
        
        Args:
            input_path: Input file path (optional)
            output_path: Output file path (optional)
            
        Returns:
            Processed DataFrame
        """
        self.logger.info("Starting preprocessing pipeline")
        
        # Load data
        self.load_data(input_path)
        
        # Clean numeric columns (remove commas, etc.)
        self.clean_numeric_columns()
        
        # Rename columns to match expected format
        self.rename_columns()
        
        # Convert dates
        self.convert_date_column()
        
        # Remove duplicates
        self.remove_duplicates()
        
        # Sort chronologically
        self.sort_chronologically()
        
        # Reset index
        self.reset_index()
        
        # Create continuous timeline
        self.create_continuous_timeline()
        
        # Forward fill missing values
        self.forward_fill_numeric()
        
        # Save processed data
        self.save_processed_data(output_path)
        
        self.logger.info("Preprocessing pipeline completed successfully")
        
        return self.df


def main():
    """
    Main function to run preprocessing pipeline.
    """
    preprocessor = DataPreprocessor()
    df = preprocessor.preprocess_pipeline()
    
    print(f"Preprocessing completed. Processed {len(df)} rows.")
    print(f"Date range: {df[preprocessor.config['data']['date_column']].min()} to {df[preprocessor.config['data']['date_column']].max()}")
    print(f"Columns: {list(df.columns)}")


if __name__ == "__main__":
    main()

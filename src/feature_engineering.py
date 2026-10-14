"""
Feature Engineering Module

This module generates derived features and temporal variables for analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.logger import get_logger
from backend.utils import load_config


class FeatureEngineer:
    """
    Feature engineering class for HHS UAC Program data.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the FeatureEngineer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or load_config()
        self.logger = get_logger(__name__)
        self.df: Optional[pd.DataFrame] = None
        
    def load_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load processed data for feature engineering.
        
        Args:
            file_path: Path to processed data file
            
        Returns:
            Loaded DataFrame
        """
        if file_path is None:
            file_path = self.config["data"]["processed_path"]
        
        self.logger.info(f"Loading data for feature engineering: {file_path}")
        
        try:
            self.df = pd.read_csv(file_path)
            # Convert date column
            date_col = self.config["data"]["date_column"]
            self.df[date_col] = pd.to_datetime(self.df[date_col])
            self.logger.info(f"Loaded {len(self.df)} rows for feature engineering")
            return self.df
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise
    
    def create_total_system_load(self) -> pd.DataFrame:
        """
        Create Total System Load feature (CBP Custody + HHS Care).
        
        Returns:
            DataFrame with new feature
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Creating Total System Load feature")
        
        # Check for both old and new column names
        cbp_col = "CBP_Custody" if "CBP_Custody" in self.df.columns else "CBP Custody"
        hhs_col = "HHS_Care" if "HHS_Care" in self.df.columns else "HHS Care"
        
        if cbp_col in self.df.columns and hhs_col in self.df.columns:
            self.df["Total_System_Load"] = self.df[cbp_col] + self.df[hhs_col]
        else:
            self.logger.warning("Required columns not found for Total System Load")
        
        return self.df
    
    def create_net_daily_intake(self) -> pd.DataFrame:
        """
        Create Net Daily Intake feature (Transfers - Discharges).
        
        Returns:
            DataFrame with new feature
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Creating Net Daily Intake feature")
        
        if "Transfers" in self.df.columns and "Discharges" in self.df.columns:
            self.df["Net_Daily_Intake"] = self.df["Transfers"] - self.df["Discharges"]
        else:
            self.logger.warning("Required columns not found for Net Daily Intake")
        
        return self.df
    
    def create_daily_growth_rate(self) -> pd.DataFrame:
        """
        Create Daily Growth Rate feature (percentage change of HHS Care).
        
        Returns:
            DataFrame with new feature
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Creating Daily Growth Rate feature")
        
        # Check for both old and new column names
        hhs_col = "HHS_Care" if "HHS_Care" in self.df.columns else "HHS Care"
        
        if hhs_col in self.df.columns:
            self.df["Daily_Growth_Rate"] = self.df[hhs_col].pct_change() * 100
            self.df["Daily_Growth_Rate"] = self.df["Daily_Growth_Rate"].fillna(0)
        else:
            self.logger.warning("Required column not found for Daily Growth Rate")
        
        return self.df
    
    def create_backlog_indicator(self) -> pd.DataFrame:
        """
        Create Backlog Indicator feature (cumulative positive net intake).
        
        Returns:
            DataFrame with new feature
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Creating Backlog Indicator feature")
        
        if "Net_Daily_Intake" not in self.df.columns:
            self.create_net_daily_intake()
        
        # Cumulative sum of positive net intake
        positive_net_intake = self.df["Net_Daily_Intake"].clip(lower=0)
        self.df["Backlog_Indicator"] = positive_net_intake.cumsum()
        
        return self.df
    
    def create_discharge_offset_ratio(self) -> pd.DataFrame:
        """
        Create Discharge Offset Ratio feature (Discharges / Transfers).
        
        Returns:
            DataFrame with new feature
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Creating Discharge Offset Ratio feature")
        
        if "Discharges" in self.df.columns and "Transfers" in self.df.columns:
            # Safe division to avoid division by zero
            self.df["Discharge_Offset_Ratio"] = np.where(
                self.df["Transfers"] > 0,
                self.df["Discharges"] / self.df["Transfers"],
                0
            )
            self.df["Discharge_Offset_Ratio"] = self.df["Discharge_Offset_Ratio"].fillna(0)
        else:
            self.logger.warning("Required columns not found for Discharge Offset Ratio")
        
        return self.df
    
    def create_rolling_features(self) -> pd.DataFrame:
        """
        Create rolling window features (mean, std, variance).
        
        Returns:
            DataFrame with new features
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Creating rolling window features")
        
        windows = self.config["features"]["rolling_windows"]
        
        # Get numeric columns (excluding date and already created features)
        date_col = self.config["data"]["date_column"]
        
        # Check for both old and new column names
        cbp_col = "CBP_Custody" if "CBP_Custody" in self.df.columns else "CBP Custody"
        hhs_col = "HHS_Care" if "HHS_Care" in self.df.columns else "HHS Care"
        
        numeric_cols = [cbp_col, "Transfers", hhs_col, "Discharges", "Total_System_Load", "Net_Daily_Intake"]
        existing_cols = [col for col in numeric_cols if col in self.df.columns]
        
        for window in windows:
            for col in existing_cols:
                # Rolling mean
                self.df[f"{col}_Rolling_Mean_{window}d"] = self.df[col].rolling(window=window, min_periods=1).mean()
                
                # Rolling standard deviation
                self.df[f"{col}_Rolling_Std_{window}d"] = self.df[col].rolling(window=window, min_periods=1).std()
                
                # Rolling variance
                self.df[f"{col}_Rolling_Var_{window}d"] = self.df[col].rolling(window=window, min_periods=1).var()
        
        return self.df
    
    def create_temporal_features(self) -> pd.DataFrame:
        """
        Create temporal features (week, month, quarter, year, day of week, weekend).
        
        Returns:
            DataFrame with new features
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Creating temporal features")
        
        date_col = self.config["data"]["date_column"]
        temporal_features = self.config["features"]["temporal_features"]
        
        if "week_number" in temporal_features:
            self.df["Week_Number"] = self.df[date_col].dt.isocalendar().week
        
        if "month" in temporal_features:
            self.df["Month"] = self.df[date_col].dt.month
        
        if "quarter" in temporal_features:
            self.df["Quarter"] = self.df[date_col].dt.quarter
        
        if "year" in temporal_features:
            self.df["Year"] = self.df[date_col].dt.year
        
        if "day_of_week" in temporal_features:
            self.df["Day_of_Week"] = self.df[date_col].dt.dayofweek
        
        if "weekend_flag" in temporal_features:
            self.df["Weekend_Flag"] = self.df[date_col].dt.dayofweek >= 5
        
        return self.df
    
    def create_all_features(self) -> pd.DataFrame:
        """
        Create all features in the correct order.
        
        Returns:
            DataFrame with all features
        """
        self.logger.info("Creating all features")
        
        # Create base derived features
        self.create_total_system_load()
        self.create_net_daily_intake()
        self.create_daily_growth_rate()
        self.create_backlog_indicator()
        self.create_discharge_offset_ratio()
        
        # Create rolling features
        self.create_rolling_features()
        
        # Create temporal features
        self.create_temporal_features()
        
        self.logger.info(f"Feature engineering completed. Total columns: {len(self.df.columns)}")
        
        return self.df
    
    def save_featured_data(self, output_path: Optional[str] = None) -> str:
        """
        Save data with engineered features.
        
        Args:
            output_path: Output file path
            
        Returns:
            Path to saved file
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if output_path is None:
            output_path = "data/processed/featured_data.csv"
        
        self.logger.info(f"Saving featured data to: {output_path}")
        
        self.df.to_csv(output_path, index=False, encoding='utf-8')
        
        self.logger.info(f"Successfully saved {len(self.df)} rows with {len(self.df.columns)} columns")
        
        return output_path
    
    def get_feature_summary(self) -> Dict[str, Any]:
        """
        Get summary of engineered features.
        
        Returns:
            Dictionary with feature summary
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        summary = {
            "total_rows": len(self.df),
            "total_columns": len(self.df.columns),
            "feature_columns": [col for col in self.df.columns if col not in 
                              ["Date", "CBP Custody", "Transfers", "HHS Care", "Discharges"]],
            "date_range": {
                "start": str(self.df[self.config["data"]["date_column"]].min()),
                "end": str(self.df[self.config["data"]["date_column"]].max())
            }
        }
        
        return summary
    
    def feature_engineering_pipeline(self, input_path: Optional[str] = None,
                                    output_path: Optional[str] = None) -> pd.DataFrame:
        """
        Run complete feature engineering pipeline.
        
        Args:
            input_path: Input file path (optional)
            output_path: Output file path (optional)
            
        Returns:
            DataFrame with engineered features
        """
        self.logger.info("Starting feature engineering pipeline")
        
        # Load data
        self.load_data(input_path)
        
        # Create all features
        self.create_all_features()
        
        # Save featured data
        self.save_featured_data(output_path)
        
        self.logger.info("Feature engineering pipeline completed successfully")
        
        return self.df


def main():
    """
    Main function to run feature engineering pipeline.
    """
    engineer = FeatureEngineer()
    df = engineer.feature_engineering_pipeline()
    
    summary = engineer.get_feature_summary()
    print(f"Feature engineering completed.")
    print(f"Total rows: {summary['total_rows']}")
    print(f"Total columns: {summary['total_columns']}")
    print(f"Feature columns: {len(summary['feature_columns'])}")
    print(f"Date range: {summary['date_range']['start']} to {summary['date_range']['end']}")


if __name__ == "__main__":
    main()

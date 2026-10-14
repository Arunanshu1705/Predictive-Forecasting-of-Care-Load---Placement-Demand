"""
KPI Calculation Module

This module computes Key Performance Indicators for the dashboard.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.logger import get_logger
from backend.utils import load_config, safe_divide, calculate_percentage


class KPICalculator:
    """
    KPI calculation class for HHS UAC Program data.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the KPICalculator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or load_config()
        self.logger = get_logger(__name__)
        self.df: Optional[pd.DataFrame] = None
        self.kpis: Dict[str, Any] = {}
        
    def load_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load featured data for KPI calculation.
        
        Args:
            file_path: Path to featured data file
            
        Returns:
            Loaded DataFrame
        """
        if file_path is None:
            file_path = "data/processed/featured_data.csv"
        
        self.logger.info(f"Loading data for KPI calculation: {file_path}")
        
        try:
            self.df = pd.read_csv(file_path, encoding='utf-8')
            # Convert date column
            date_col = self.config["data"]["date_column"]
            self.df[date_col] = pd.to_datetime(self.df[date_col])
            self.logger.info(f"Loaded {len(self.df)} rows for KPI calculation")
            return self.df
        except UnicodeDecodeError:
            self.df = pd.read_csv(file_path, encoding='latin1')
            date_col = self.config["data"]["date_column"]
            self.df[date_col] = pd.to_datetime(self.df[date_col])
            self.logger.info(f"Loaded {len(self.df)} rows for KPI calculation with latin1 encoding")
            return self.df
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise
    
    def calculate_total_children_under_care(self) -> float:
        """
        Calculate Total Children Under Care (latest HHS Care value).
        
        Returns:
            Total children under care
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        # Check for both old and new column names
        hhs_col = "HHS_Care" if "HHS_Care" in self.df.columns else "HHS Care"
        
        if hhs_col in self.df.columns:
            value = self.df[hhs_col].iloc[-1]
            self.kpis["total_children_under_care"] = float(value)
            return value
        return 0.0
    
    def calculate_average_daily_intake(self) -> float:
        """
        Calculate Average Daily Intake (mean of Transfers).
        
        Returns:
            Average daily intake
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if "Transfers" in self.df.columns:
            value = self.df["Transfers"].mean()
            self.kpis["average_daily_intake"] = float(value)
            return value
        return 0.0
    
    def calculate_average_daily_discharges(self) -> float:
        """
        Calculate Average Daily Discharges (mean of Discharges).
        
        Returns:
            Average daily discharges
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if "Discharges" in self.df.columns:
            value = self.df["Discharges"].mean()
            self.kpis["average_daily_discharges"] = float(value)
            return value
        return 0.0
    
    def calculate_average_cbp_load(self) -> float:
        """
        Calculate Average CBP Load (mean of CBP Custody).
        
        Returns:
            Average CBP load
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        # Check for both old and new column names
        cbp_col = "CBP_Custody" if "CBP_Custody" in self.df.columns else "CBP Custody"
        
        if cbp_col in self.df.columns:
            value = self.df[cbp_col].mean()
            self.kpis["average_cbp_load"] = float(value)
            return value
        return 0.0
    
    def calculate_average_hhs_load(self) -> float:
        """
        Calculate Average HHS Load (mean of HHS Care).
        
        Returns:
            Average HHS load
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        # Check for both old and new column names
        hhs_col = "HHS_Care" if "HHS_Care" in self.df.columns else "HHS Care"
        
        if hhs_col in self.df.columns:
            value = self.df[hhs_col].mean()
            self.kpis["average_hhs_load"] = float(value)
            return value
        return 0.0
    
    def calculate_net_intake_pressure(self) -> float:
        """
        Calculate Net Intake Pressure (mean of Net Daily Intake).
        
        Returns:
            Net intake pressure
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if "Net_Daily_Intake" in self.df.columns:
            value = self.df["Net_Daily_Intake"].mean()
            self.kpis["net_intake_pressure"] = float(value)
            return value
        elif "Transfers" in self.df.columns and "Discharges" in self.df.columns:
            value = (self.df["Transfers"] - self.df["Discharges"]).mean()
            self.kpis["net_intake_pressure"] = float(value)
            return value
        return 0.0
    
    def calculate_care_load_volatility_index(self) -> float:
        """
        Calculate Care Load Volatility Index (std dev of HHS Care / mean).
        
        Returns:
            Care load volatility index
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        # Check for both old and new column names
        hhs_col = "HHS_Care" if "HHS_Care" in self.df.columns else "HHS Care"
        
        if hhs_col in self.df.columns:
            std = self.df[hhs_col].std()
            mean = self.df[hhs_col].mean()
            value = safe_divide(std, mean, 0.0)
            self.kpis["care_load_volatility_index"] = float(value)
            return value
        return 0.0
    
    def calculate_backlog_accumulation_rate(self) -> float:
        """
        Calculate Backlog Accumulation Rate (slope of Backlog Indicator).
        
        Returns:
            Backlog accumulation rate
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if "Backlog_Indicator" in self.df.columns:
            # Calculate rate as change per day
            value = self.df["Backlog_Indicator"].diff().mean()
            self.kpis["backlog_accumulation_rate"] = float(value)
            return value
        return 0.0
    
    def calculate_discharge_offset_ratio(self) -> float:
        """
        Calculate Discharge Offset Ratio (mean of Discharge Offset Ratio).
        
        Returns:
            Discharge offset ratio
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if "Discharge_Offset_Ratio" in self.df.columns:
            value = self.df["Discharge_Offset_Ratio"].mean()
            self.kpis["discharge_offset_ratio"] = float(value)
            return value
        elif "Discharges" in self.df.columns and "Transfers" in self.df.columns:
            value = safe_divide(self.df["Discharges"].sum(), self.df["Transfers"].sum(), 0.0)
            self.kpis["discharge_offset_ratio"] = float(value)
            return value
        return 0.0
    
    def calculate_peak_load_day(self) -> Dict[str, Any]:
        """
        Calculate Peak Load Day (max Total System Load).
        
        Returns:
            Dictionary with peak load day information
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        date_col = self.config["data"]["date_column"]
        
        # Check for both old and new column names
        hhs_col = "HHS_Care" if "HHS_Care" in self.df.columns else "HHS Care"
        cbp_col = "CBP_Custody" if "CBP_Custody" in self.df.columns else "CBP Custody"
        
        if "Total_System_Load" in self.df.columns:
            max_idx = self.df["Total_System_Load"].idxmax()
            result = {
                "date": str(self.df.loc[max_idx, date_col]),
                "value": float(self.df.loc[max_idx, "Total_System_Load"])
            }
        elif hhs_col in self.df.columns:
            max_idx = self.df[hhs_col].idxmax()
            result = {
                "date": str(self.df.loc[max_idx, date_col]),
                "value": float(self.df.loc[max_idx, hhs_col])
            }
        else:
            result = {"date": "N/A", "value": 0.0}
        
        self.kpis["peak_load_day"] = result
        return result
    
    def calculate_lowest_load_day(self) -> Dict[str, Any]:
        """
        Calculate Lowest Load Day (min Total System Load).
        
        Returns:
            Dictionary with lowest load day information
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        date_col = self.config["data"]["date_column"]
        
        # Check for both old and new column names
        hhs_col = "HHS_Care" if "HHS_Care" in self.df.columns else "HHS Care"
        
        if "Total_System_Load" in self.df.columns:
            min_idx = self.df["Total_System_Load"].idxmin()
            result = {
                "date": str(self.df.loc[min_idx, date_col]),
                "value": float(self.df.loc[min_idx, "Total_System_Load"])
            }
        elif hhs_col in self.df.columns:
            min_idx = self.df[hhs_col].idxmin()
            result = {
                "date": str(self.df.loc[min_idx, date_col]),
                "value": float(self.df.loc[min_idx, hhs_col])
            }
        else:
            result = {"date": "N/A", "value": 0.0}
        
        self.kpis["lowest_load_day"] = result
        return result
    
    def calculate_highest_intake(self) -> Dict[str, Any]:
        """
        Calculate Highest Intake (max Transfers).
        
        Returns:
            Dictionary with highest intake information
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        date_col = self.config["data"]["date_column"]
        
        if "Transfers" in self.df.columns:
            max_idx = self.df["Transfers"].idxmax()
            result = {
                "date": str(self.df.loc[max_idx, date_col]),
                "value": float(self.df.loc[max_idx, "Transfers"])
            }
        else:
            result = {"date": "N/A", "value": 0.0}
        
        self.kpis["highest_intake"] = result
        return result
    
    def calculate_highest_discharge(self) -> Dict[str, Any]:
        """
        Calculate Highest Discharge (max Discharges).
        
        Returns:
            Dictionary with highest discharge information
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        date_col = self.config["data"]["date_column"]
        
        if "Discharges" in self.df.columns:
            max_idx = self.df["Discharges"].idxmax()
            result = {
                "date": str(self.df.loc[max_idx, date_col]),
                "value": float(self.df.loc[max_idx, "Discharges"])
            }
        else:
            result = {"date": "N/A", "value": 0.0}
        
        self.kpis["highest_discharge"] = result
        return result
    
    def calculate_average_system_load(self) -> float:
        """
        Calculate Average System Load (mean of Total System Load).
        
        Returns:
            Average system load
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        if "Total_System_Load" in self.df.columns:
            value = self.df["Total_System_Load"].mean()
            self.kpis["average_system_load"] = float(value)
            return value
        else:
            # Check for both old and new column names
            hhs_col = "HHS_Care" if "HHS_Care" in self.df.columns else "HHS Care"
            cbp_col = "CBP_Custody" if "CBP_Custody" in self.df.columns else "CBP Custody"
            
            if hhs_col in self.df.columns and cbp_col in self.df.columns:
                value = (self.df[hhs_col] + self.df[cbp_col]).mean()
                self.kpis["average_system_load"] = float(value)
                return value
        return 0.0
    
    def calculate_all_kpis(self) -> Dict[str, Any]:
        """
        Calculate all KPIs.
        
        Returns:
            Dictionary with all KPIs
        """
        self.logger.info("Calculating all KPIs")
        
        # Calculate all KPIs
        self.calculate_total_children_under_care()
        self.calculate_average_daily_intake()
        self.calculate_average_daily_discharges()
        self.calculate_average_cbp_load()
        self.calculate_average_hhs_load()
        self.calculate_net_intake_pressure()
        self.calculate_care_load_volatility_index()
        self.calculate_backlog_accumulation_rate()
        self.calculate_discharge_offset_ratio()
        self.calculate_peak_load_day()
        self.calculate_lowest_load_day()
        self.calculate_highest_intake()
        self.calculate_highest_discharge()
        self.calculate_average_system_load()
        
        # Add metadata
        self.kpis["calculation_timestamp"] = datetime.now().isoformat()
        self.kpis["data_period"] = {
            "start": str(self.df[self.config["data"]["date_column"]].min()),
            "end": str(self.df[self.config["data"]["date_column"]].max()),
            "total_days": len(self.df)
        }
        
        self.logger.info(f"Calculated {len(self.kpis)} KPIs")
        
        return self.kpis
    
    def get_kpi_summary(self) -> str:
        """
        Get a human-readable KPI summary.
        
        Returns:
            Summary string
        """
        if not self.kpis:
            return "No KPIs calculated. Run calculate_all_kpis() first."
        
        summary = []
        summary.append("=" * 60)
        summary.append("KEY PERFORMANCE INDICATORS")
        summary.append("=" * 60)
        summary.append(f"Calculation Timestamp: {self.kpis.get('calculation_timestamp', 'N/A')}")
        summary.append(f"Data Period: {self.kpis.get('data_period', {}).get('start', 'N/A')} to {self.kpis.get('data_period', {}).get('end', 'N/A')}")
        summary.append(f"Total Days: {self.kpis.get('data_period', {}).get('total_days', 0)}")
        summary.append("")
        
        summary.append("CURRENT STATUS:")
        summary.append(f"  Total Children Under Care: {self.kpis.get('total_children_under_care', 0):,.0f}")
        summary.append(f"  Average System Load: {self.kpis.get('average_system_load', 0):,.0f}")
        summary.append("")
        
        summary.append("DAILY AVERAGES:")
        summary.append(f"  Average Daily Intake: {self.kpis.get('average_daily_intake', 0):,.0f}")
        summary.append(f"  Average Daily Discharges: {self.kpis.get('average_daily_discharges', 0):,.0f}")
        summary.append(f"  Average CBP Load: {self.kpis.get('average_cbp_load', 0):,.0f}")
        summary.append(f"  Average HHS Load: {self.kpis.get('average_hhs_load', 0):,.0f}")
        summary.append("")
        
        summary.append("PRESSURE INDICATORS:")
        summary.append(f"  Net Intake Pressure: {self.kpis.get('net_intake_pressure', 0):,.0f}")
        summary.append(f"  Care Load Volatility Index: {self.kpis.get('care_load_volatility_index', 0):.3f}")
        summary.append(f"  Backlog Accumulation Rate: {self.kpis.get('backlog_accumulation_rate', 0):,.0f}/day")
        summary.append(f"  Discharge Offset Ratio: {self.kpis.get('discharge_offset_ratio', 0):.3f}")
        summary.append("")
        
        summary.append("EXTREME VALUES:")
        peak = self.kpis.get('peak_load_day', {})
        summary.append(f"  Peak Load Day: {peak.get('date', 'N/A')} ({peak.get('value', 0):,.0f})")
        lowest = self.kpis.get('lowest_load_day', {})
        summary.append(f"  Lowest Load Day: {lowest.get('date', 'N/A')} ({lowest.get('value', 0):,.0f})")
        highest_intake = self.kpis.get('highest_intake', {})
        summary.append(f"  Highest Intake: {highest_intake.get('date', 'N/A')} ({highest_intake.get('value', 0):,.0f})")
        highest_discharge = self.kpis.get('highest_discharge', {})
        summary.append(f"  Highest Discharge: {highest_discharge.get('date', 'N/A')} ({highest_discharge.get('value', 0):,.0f})")
        
        summary.append("=" * 60)
        
        return "\n".join(summary)
    
    def save_kpis(self, output_path: Optional[str] = None) -> str:
        """
        Save KPIs to JSON file.
        
        Args:
            output_path: Output file path
            
        Returns:
            Path to saved file
        """
        import json
        
        if not self.kpis:
            raise ValueError("No KPIs calculated. Run calculate_all_kpis() first.")
        
        if output_path is None:
            output_path = "reports/kpis.json"
        
        self.logger.info(f"Saving KPIs to: {output_path}")
        
        with open(output_path, 'w') as f:
            json.dump(self.kpis, f, indent=2, default=str)
        
        self.logger.info("KPIs saved successfully")
        
        return output_path


def main():
    """
    Main function to run KPI calculation pipeline.
    """
    calculator = KPICalculator()
    calculator.load_data()
    kpis = calculator.calculate_all_kpis()
    
    print(calculator.get_kpi_summary())
    
    # Save KPIs
    calculator.save_kpis()
    print("\nKPIs saved to: reports/kpis.json")


if __name__ == "__main__":
    main()

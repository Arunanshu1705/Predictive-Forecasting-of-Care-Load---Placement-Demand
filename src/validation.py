"""
Data Validation Module

This module performs automated validation checks on the dataset.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import sys
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.logger import get_logger
from backend.utils import load_config, ensure_directory


class DataValidator:
    """
    Data validation class for HHS UAC Program data.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the DataValidator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or load_config()
        self.logger = get_logger(__name__)
        self.df: Optional[pd.DataFrame] = None
        self.validation_results: Dict[str, Any] = {}
        
    def load_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load processed data for validation.
        
        Args:
            file_path: Path to processed data file
            
        Returns:
            Loaded DataFrame
        """
        if file_path is None:
            file_path = self.config["data"]["processed_path"]
        
        self.logger.info(f"Loading data for validation: {file_path}")
        
        try:
            self.df = pd.read_csv(file_path, encoding='utf-8')
            # Convert date column
            date_col = self.config["data"]["date_column"]
            self.df[date_col] = pd.to_datetime(self.df[date_col])
            self.logger.info(f"Loaded {len(self.df)} rows for validation")
            return self.df
        except UnicodeDecodeError:
            self.df = pd.read_csv(file_path, encoding='latin1')
            date_col = self.config["data"]["date_column"]
            self.df[date_col] = pd.to_datetime(self.df[date_col])
            self.logger.info(f"Loaded {len(self.df)} rows for validation with latin1 encoding")
            return self.df
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise
    
    def check_missing_values(self) -> Dict[str, Any]:
        """
        Check for missing values in the dataset.
        
        Returns:
            Dictionary with missing value information
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Checking for missing values")
        
        missing_counts = self.df.isnull().sum()
        missing_percentages = (missing_counts / len(self.df)) * 100
        
        result = {
            "has_missing": missing_counts.sum() > 0,
            "missing_counts": missing_counts.to_dict(),
            "missing_percentages": missing_percentages.to_dict(),
            "total_missing": int(missing_counts.sum()),
            "status": "PASS" if missing_counts.sum() == 0 else "WARNING"
        }
        
        self.validation_results["missing_values"] = result
        
        if result["has_missing"]:
            self.logger.warning(f"Found {result['total_missing']} missing values")
        else:
            self.logger.info("No missing values found")
        
        return result
    
    def check_duplicate_dates(self) -> Dict[str, Any]:
        """
        Check for duplicate dates in the dataset.
        
        Returns:
            Dictionary with duplicate date information
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Checking for duplicate dates")
        
        date_col = self.config["data"]["date_column"]
        duplicates = self.df.duplicated(subset=[date_col]).sum()
        
        result = {
            "has_duplicates": duplicates > 0,
            "duplicate_count": int(duplicates),
            "duplicate_percentage": (duplicates / len(self.df)) * 100,
            "status": "PASS" if duplicates == 0 else "FAIL"
        }
        
        self.validation_results["duplicate_dates"] = result
        
        if result["has_duplicates"]:
            self.logger.error(f"Found {duplicates} duplicate dates")
        else:
            self.logger.info("No duplicate dates found")
        
        return result
    
    def check_transfers_le_cbp(self) -> Dict[str, Any]:
        """
        Check if Transfers <= CBP Custody for all records.
        
        Returns:
            Dictionary with validation result
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Checking Transfers <= CBP Custody")
        
        # Check for both old and new column names
        cbp_col = "CBP_Custody" if "CBP_Custody" in self.df.columns else "CBP Custody"
        transfers_col = "Transfers"
        
        if transfers_col not in self.df.columns or cbp_col not in self.df.columns:
            self.logger.warning("Required columns not found for this check")
            return {"status": "SKIPPED", "reason": "Required columns not found"}
        
        violations = (self.df[transfers_col] > self.df[cbp_col]).sum()
        
        result = {
            "has_violations": violations > 0,
            "violation_count": int(violations),
            "violation_percentage": (violations / len(self.df)) * 100,
            "status": "PASS" if violations == 0 else "FAIL"
        }
        
        self.validation_results["transfers_le_cbp"] = result
        
        if result["has_violations"]:
            self.logger.error(f"Found {violations} violations of Transfers <= CBP Custody")
        else:
            self.logger.info("All Transfers <= CBP Custody")
        
        return result
    
    def check_discharges_le_hhs(self) -> Dict[str, Any]:
        """
        Check if Discharges <= HHS Care for all records.
        
        Returns:
            Dictionary with validation result
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Checking Discharges <= HHS Care")
        
        # Check for both old and new column names
        hhs_col = "HHS_Care" if "HHS_Care" in self.df.columns else "HHS Care"
        discharges_col = "Discharges"
        
        if discharges_col not in self.df.columns or hhs_col not in self.df.columns:
            self.logger.warning("Required columns not found for this check")
            return {"status": "SKIPPED", "reason": "Required columns not found"}
        
        violations = (self.df[discharges_col] > self.df[hhs_col]).sum()
        
        result = {
            "has_violations": violations > 0,
            "violation_count": int(violations),
            "violation_percentage": (violations / len(self.df)) * 100,
            "status": "PASS" if violations == 0 else "FAIL"
        }
        
        self.validation_results["discharges_le_hhs"] = result
        
        if result["has_violations"]:
            self.logger.error(f"Found {violations} violations of Discharges <= HHS Care")
        else:
            self.logger.info("All Discharges <= HHS Care")
        
        return result
    
    def check_negative_values(self) -> Dict[str, Any]:
        """
        Check for negative values in numeric columns.
        
        Returns:
            Dictionary with negative value information
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Checking for negative values")
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        negative_counts = {}
        
        for col in numeric_cols:
            negative_counts[col] = (self.df[col] < 0).sum()
        
        total_negatives = sum(negative_counts.values())
        
        result = {
            "has_negatives": total_negatives > 0,
            "negative_counts": negative_counts,
            "total_negatives": int(total_negatives),
            "status": "PASS" if total_negatives == 0 else "FAIL"
        }
        
        self.validation_results["negative_values"] = result
        
        if result["has_negatives"]:
            self.logger.error(f"Found {total_negatives} negative values")
        else:
            self.logger.info("No negative values found")
        
        return result
    
    def check_reporting_anomalies(self) -> Dict[str, Any]:
        """
        Check for reporting anomalies (unusual changes, zeros, etc.).
        
        Returns:
            Dictionary with anomaly information
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Checking for reporting anomalies")
        
        result = {
            "has_anomalies": False,
            "anomalies": {"large_changes": [], "extended_zeros": {}},
            "status": "PASS"
        }
        
        try:
            threshold = self.config["validation"]["anomaly_thresholds"]["daily_change_percent"]
            zero_threshold = self.config["validation"]["anomaly_thresholds"]["zero_consecutive_days"]
            
            anomalies = {
                "large_changes": [],
                "extended_zeros": {}
            }
            
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            
            # Check for large daily changes
            for col in numeric_cols:
                daily_change = self.df[col].pct_change().abs() * 100
                large_changes = daily_change[daily_change > threshold]
                
                if len(large_changes) > 0:
                    anomalies["large_changes"].append({
                        "column": col,
                        "count": len(large_changes),
                        "max_change": float(large_changes.max()),
                        "dates": large_changes.index.tolist()[:10]  # First 10
                    })
            
            # Check for extended zeros
            for col in numeric_cols:
                zero_runs = []
                current_run = 0
                
                for val in self.df[col]:
                    if val == 0:
                        current_run += 1
                    else:
                        if current_run >= zero_threshold:
                            zero_runs.append(current_run)
                        current_run = 0
                
                if current_run >= zero_threshold:
                    zero_runs.append(current_run)
                
                if zero_runs:
                    anomalies["extended_zeros"][col] = {
                        "runs": zero_runs,
                        "max_run": max(zero_runs),
                        "total_runs": len(zero_runs)
                    }
            
            result = {
                "has_anomalies": len(anomalies["large_changes"]) > 0 or len(anomalies["extended_zeros"]) > 0,
                "anomalies": anomalies,
                "status": "PASS" if not result["has_anomalies"] else "WARNING"
            }
            
        except Exception as e:
            self.logger.error(f"Error checking reporting anomalies: {str(e)}")
            result["status"] = "ERROR"
            result["error"] = str(e)
        
        self.validation_results["reporting_anomalies"] = result
        
        if result["has_anomalies"]:
            self.logger.warning(f"Found reporting anomalies")
        else:
            self.logger.info("No reporting anomalies found")
        
        return result
    
    def run_all_validations(self) -> Dict[str, Any]:
        """
        Run all validation checks.
        
        Returns:
            Dictionary with all validation results
        """
        self.logger.info("Running all validation checks")
        
        config = self.config["validation"]
        
        results = {}
        
        if config["check_missing_values"]:
            results["missing_values"] = self.check_missing_values()
        
        if config["check_duplicate_dates"]:
            results["duplicate_dates"] = self.check_duplicate_dates()
        
        if config["check_transfers_le_cbp"]:
            results["transfers_le_cbp"] = self.check_transfers_le_cbp()
        
        if config["check_discharges_le_hhs"]:
            results["discharges_le_hhs"] = self.check_discharges_le_hhs()
        
        if config["check_negative_values"]:
            results["negative_values"] = self.check_negative_values()
        
        if config["check_reporting_anomalies"]:
            results["reporting_anomalies"] = self.check_reporting_anomalies()
        
        # Calculate overall status
        failed_checks = [k for k, v in results.items() if v.get("status") == "FAIL"]
        warning_checks = [k for k, v in results.items() if v.get("status") == "WARNING"]
        
        overall_status = "PASS"
        if failed_checks:
            overall_status = "FAIL"
        elif warning_checks:
            overall_status = "WARNING"
        
        results["overall_status"] = overall_status
        results["failed_checks"] = failed_checks
        results["warning_checks"] = warning_checks
        results["validation_timestamp"] = datetime.now().isoformat()
        
        self.validation_results = results
        
        self.logger.info(f"Validation completed with status: {overall_status}")
        
        return results
    
    def save_validation_report(self, output_path: Optional[str] = None) -> str:
        """
        Save validation report to JSON file.
        
        Args:
            output_path: Output file path
            
        Returns:
            Path to saved report
        """
        if not self.validation_results:
            raise ValueError("No validation results. Run validations first.")
        
        if output_path is None:
            output_path = "reports/validation_report.json"
        
        # Ensure output directory exists
        output_file = Path(output_path)
        ensure_directory(str(output_file.parent))
        
        self.logger.info(f"Saving validation report to: {output_path}")
        
        with open(output_path, 'w') as f:
            json.dump(self.validation_results, f, indent=2, default=str)
        
        self.logger.info("Validation report saved successfully")
        
        return output_path
    
    def get_validation_summary(self) -> str:
        """
        Get a human-readable validation summary.
        
        Returns:
            Summary string
        """
        if not self.validation_results:
            return "No validation results available."
        
        summary = []
        summary.append("=" * 60)
        summary.append("DATA VALIDATION REPORT")
        summary.append("=" * 60)
        summary.append(f"Validation Timestamp: {self.validation_results.get('validation_timestamp', 'N/A')}")
        summary.append(f"Overall Status: {self.validation_results.get('overall_status', 'N/A')}")
        summary.append("")
        
        if self.validation_results.get("failed_checks"):
            summary.append("FAILED CHECKS:")
            for check in self.validation_results["failed_checks"]:
                summary.append(f"  - {check}")
            summary.append("")
        
        if self.validation_results.get("warning_checks"):
            summary.append("WARNING CHECKS:")
            for check in self.validation_results["warning_checks"]:
                summary.append(f"  - {check}")
            summary.append("")
        
        summary.append("DETAILED RESULTS:")
        for check_name, result in self.validation_results.items():
            if check_name in ["overall_status", "failed_checks", "warning_checks", "validation_timestamp"]:
                continue
            summary.append(f"\n{check_name.upper()}:")
            summary.append(f"  Status: {result.get('status', 'N/A')}")
            if result.get("has_missing"):
                summary.append(f"  Total Missing: {result.get('total_missing', 0)}")
            if result.get("has_duplicates"):
                summary.append(f"  Duplicate Count: {result.get('duplicate_count', 0)}")
            if result.get("has_violations"):
                summary.append(f"  Violation Count: {result.get('violation_count', 0)}")
            if result.get("has_negatives"):
                summary.append(f"  Total Negatives: {result.get('total_negatives', 0)}")
            if result.get("has_anomalies"):
                summary.append(f"  Anomalies Detected: Yes")
        
        summary.append("=" * 60)
        
        return "\n".join(summary)


def main():
    """
    Main function to run validation pipeline.
    """
    validator = DataValidator()
    validator.load_data()
    results = validator.run_all_validations()
    
    print(validator.get_validation_summary())
    
    # Save report
    validator.save_validation_report()
    print("\nValidation report saved to: reports/validation_report.json")


if __name__ == "__main__":
    main()

"""
Healthcare Analytics Module

This module implements specialized analytics for capacity stress, backlog analysis,
and pressure detection in the UAC Program.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.logger import get_logger
from backend.utils import load_config, safe_divide


class HealthcareAnalytics:
    """
    Healthcare analytics class for HHS UAC Program data.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the HealthcareAnalytics.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or load_config()
        self.logger = get_logger(__name__)
        self.df: Optional[pd.DataFrame] = None
        self.analytics_results: Dict[str, Any] = {}
        
    def load_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load featured data for analytics.
        
        Args:
            file_path: Path to featured data file
            
        Returns:
            Loaded DataFrame
        """
        if file_path is None:
            file_path = "data/processed/featured_data.csv"
        
        self.logger.info(f"Loading data for analytics: {file_path}")
        
        try:
            self.df = pd.read_csv(file_path, encoding='utf-8')
            # Convert date column
            date_col = self.config["data"]["date_column"]
            self.df[date_col] = pd.to_datetime(self.df[date_col])
            self.logger.info(f"Loaded {len(self.df)} rows for analytics")
            return self.df
        except UnicodeDecodeError:
            self.df = pd.read_csv(file_path, encoding='latin1')
            date_col = self.config["data"]["date_column"]
            self.df[date_col] = pd.to_datetime(self.df[date_col])
            self.logger.info(f"Loaded {len(self.df)} rows for analytics with latin1 encoding")
            return self.df
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise
    
    def detect_capacity_stress(self) -> Dict[str, Any]:
        """
        Detect capacity stress periods based on thresholds.
        
        Returns:
            Dictionary with capacity stress analysis
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Detecting capacity stress periods")
        
        date_col = self.config["data"]["date_column"]
        threshold_percent = self.config["analytics"]["capacity_stress"]["threshold_percent"]
        
        # Calculate threshold based on historical maximum
        if "Total_System_Load" in self.df.columns:
            max_load = self.df["Total_System_Load"].max()
            threshold = max_load * threshold_percent
            load_col = "Total_System_Load"
        elif "HHS_Care" in self.df.columns:
            max_load = self.df["HHS_Care"].max()
            threshold = max_load * threshold_percent
            load_col = "HHS_Care"
        elif "HHS_Care" in self.df.columns:
            max_load = self.df["HHS_Care"].max()
            threshold = max_load * threshold_percent
            load_col = "HHS_Care"
        elif "HHS Care" in self.df.columns:
            max_load = self.df["HHS Care"].max()
            threshold = max_load * threshold_percent
            load_col = "HHS Care"
        else:
            self.logger.warning("No load column found for capacity stress detection")
            return {"status": "SKIPPED", "reason": "No load column found"}
        
        # Identify stress periods
        self.df["Capacity_Stress"] = self.df[load_col] > threshold
        stress_periods = self.df[self.df["Capacity_Stress"]]
        
        # Calculate stress statistics
        stress_days = len(stress_periods)
        stress_percentage = (stress_days / len(self.df)) * 100
        
        # Find continuous stress periods
        stress_periods_list = []
        if stress_days > 0:
            current_period = []
            for idx, row in self.df.iterrows():
                if row["Capacity_Stress"]:
                    current_period.append(row[date_col])
                else:
                    if len(current_period) > 0:
                        stress_periods_list.append({
                            "start": str(current_period[0]),
                            "end": str(current_period[-1]),
                            "duration_days": len(current_period)
                        })
                        current_period = []
            
            if len(current_period) > 0:
                stress_periods_list.append({
                    "start": str(current_period[0]),
                    "end": str(current_period[-1]),
                    "duration_days": len(current_period)
                })
        
        result = {
            "threshold": float(threshold),
            "stress_days": stress_days,
            "stress_percentage": float(stress_percentage),
            "stress_periods": stress_periods_list,
            "max_stress_duration": max([p["duration_days"] for p in stress_periods_list]) if stress_periods_list else 0,
            "status": "HIGH_STRESS" if stress_percentage > 20 else "MODERATE_STRESS" if stress_percentage > 10 else "LOW_STRESS"
        }
        
        self.analytics_results["capacity_stress"] = result
        
        self.logger.info(f"Capacity stress detection completed: {result['status']}")
        
        return result
    
    def analyze_backlog(self) -> Dict[str, Any]:
        """
        Analyze backlog accumulation and trends.
        
        Returns:
            Dictionary with backlog analysis
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Analyzing backlog")
        
        accumulation_window = self.config["analytics"]["backlog"]["accumulation_window"]
        
        if "Backlog_Indicator" not in self.df.columns:
            self.logger.warning("Backlog_Indicator column not found")
            return {"status": "SKIPPED", "reason": "Backlog_Indicator column not found"}
        
        # Calculate backlog statistics
        current_backlog = self.df["Backlog_Indicator"].iloc[-1]
        max_backlog = self.df["Backlog_Indicator"].max()
        avg_backlog = self.df["Backlog_Indicator"].mean()
        
        # Calculate backlog trend (last 30 days vs previous 30 days)
        date_col = self.config["data"]["date_column"]
        recent_period = self.df.tail(accumulation_window)
        previous_period = self.df.iloc[-(accumulation_window*2):-accumulation_window]
        
        recent_avg = recent_period["Backlog_Indicator"].mean() if len(recent_period) > 0 else 0
        previous_avg = previous_period["Backlog_Indicator"].mean() if len(previous_period) > 0 else 0
        backlog_trend = recent_avg - previous_avg
        
        # Identify increasing backlog periods
        self.df["Backlog_Change"] = self.df["Backlog_Indicator"].diff()
        increasing_periods = self.df[self.df["Backlog_Change"] > 0]
        
        result = {
            "current_backlog": float(current_backlog),
            "max_backlog": float(max_backlog),
            "avg_backlog": float(avg_backlog),
            "backlog_trend": float(backlog_trend),
            "trend_status": "INCREASING" if backlog_trend > 0 else "DECREASING" if backlog_trend < 0 else "STABLE",
            "increasing_days": len(increasing_periods),
            "accumulation_rate": float(backlog_trend / accumulation_window) if accumulation_window > 0 else 0.0
        }
        
        self.analytics_results["backlog_analysis"] = result
        
        self.logger.info(f"Backlog analysis completed: {result['trend_status']}")
        
        return result
    
    def analyze_pressure_windows(self) -> Dict[str, Any]:
        """
        Analyze pressure windows using different time windows.
        
        Returns:
            Dictionary with pressure window analysis
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Analyzing pressure windows")
        
        windows = self.config["analytics"]["pressure_windows"]
        
        if "Net_Daily_Intake" not in self.df.columns:
            self.logger.warning("Net_Daily_Intake column not found")
            return {"status": "SKIPPED", "reason": "Net_Daily_Intake column not found"}
        
        pressure_analysis = {}
        
        for window in windows:
            # Calculate rolling mean and std for the window
            rolling_mean = self.df["Net_Daily_Intake"].rolling(window=window, min_periods=1).mean()
            rolling_std = self.df["Net_Daily_Intake"].rolling(window=window, min_periods=1).std()
            
            # Identify high pressure periods (mean + 1 std)
            threshold = rolling_mean + rolling_std
            high_pressure = self.df["Net_Daily_Intake"] > threshold
            
            # Calculate statistics
            high_pressure_days = high_pressure.sum()
            avg_pressure = rolling_mean.mean()
            max_pressure = rolling_mean.max()
            
            pressure_analysis[f"{window}_day"] = {
                "average_pressure": float(avg_pressure),
                "max_pressure": float(max_pressure),
                "high_pressure_days": int(high_pressure_days),
                "high_pressure_percentage": float((high_pressure_days / len(self.df)) * 100)
            }
        
        result = {
            "windows": pressure_analysis,
            "overall_pressure_status": self._determine_pressure_status(pressure_analysis)
        }
        
        self.analytics_results["pressure_windows"] = result
        
        self.logger.info("Pressure windows analysis completed")
        
        return result
    
    def _determine_pressure_status(self, pressure_analysis: Dict[str, Any]) -> str:
        """
        Determine overall pressure status from window analysis.
        
        Args:
            pressure_analysis: Pressure analysis results
            
        Returns:
            Pressure status string
        """
        high_pressure_percentages = [v["high_pressure_percentage"] for v in pressure_analysis.values()]
        avg_percentage = np.mean(high_pressure_percentages)
        
        if avg_percentage > 30:
            return "CRITICAL"
        elif avg_percentage > 20:
            return "HIGH"
        elif avg_percentage > 10:
            return "MODERATE"
        else:
            return "LOW"
    
    def analyze_net_intake_trend(self) -> Dict[str, Any]:
        """
        Analyze net intake trend over time.
        
        Returns:
            Dictionary with net intake trend analysis
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Analyzing net intake trend")
        
        if "Net_Daily_Intake" not in self.df.columns:
            self.logger.warning("Net_Daily_Intake column not found")
            return {"status": "SKIPPED", "reason": "Net_Daily_Intake column not found"}
        
        # Calculate trend using linear regression
        x = np.arange(len(self.df))
        y = self.df["Net_Daily_Intake"].values
        
        # Remove NaN values
        mask = ~np.isnan(y)
        x = x[mask]
        y = y[mask]
        
        if len(x) < 2:
            return {"status": "INSUFFICIENT_DATA", "reason": "Not enough data points"}
        
        # Calculate slope (trend)
        slope = np.polyfit(x, y, 1)[0]
        
        # Calculate moving averages
        ma_7 = self.df["Net_Daily_Intake"].rolling(window=7, min_periods=1).mean()
        ma_14 = self.df["Net_Daily_Intake"].rolling(window=14, min_periods=1).mean()
        
        # Current vs historical comparison
        current_value = self.df["Net_Daily_Intake"].iloc[-1]
        historical_avg = self.df["Net_Daily_Intake"].mean()
        
        result = {
            "trend_slope": float(slope),
            "trend_direction": "INCREASING" if slope > 0 else "DECREASING" if slope < 0 else "STABLE",
            "current_value": float(current_value),
            "historical_average": float(historical_avg),
            "deviation_from_average": float(current_value - historical_avg),
            "ma_7_current": float(ma_7.iloc[-1]),
            "ma_14_current": float(ma_14.iloc[-1]),
            "status": "HIGH_PRESSURE" if current_value > historical_avg * 1.5 else "LOW_PRESSURE" if current_value < historical_avg * 0.5 else "NORMAL"
        }
        
        self.analytics_results["net_intake_trend"] = result
        
        self.logger.info(f"Net intake trend analysis completed: {result['trend_direction']}")
        
        return result
    
    def analyze_growth_trend(self) -> Dict[str, Any]:
        """
        Analyze growth trend of HHS Care population.
        
        Returns:
            Dictionary with growth trend analysis
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Analyzing growth trend")
        
        # Check for both old and new column names
        hhs_col = "HHS_Care" if "HHS_Care" in self.df.columns else "HHS Care"
        
        if hhs_col not in self.df.columns:
            self.logger.warning("HHS Care column not found")
            return {"status": "SKIPPED", "reason": "HHS Care column not found"}
        
        # Calculate growth rate
        self.df["Growth_Rate"] = self.df[hhs_col].pct_change() * 100
        
        # Overall growth
        start_value = self.df[hhs_col].iloc[0]
        end_value = self.df[hhs_col].iloc[-1]
        total_growth = ((end_value - start_value) / start_value) * 100 if start_value > 0 else 0
        
        # Average daily growth
        avg_daily_growth = self.df["Growth_Rate"].mean()
        
        # Growth volatility
        growth_volatility = self.df["Growth_Rate"].std()
        
        # Identify accelerating growth periods
        if "Growth_Rate_Rolling_Mean_7d" in self.df.columns:
            accelerating = self.df["Growth_Rate_Rolling_Mean_7d"].diff() > 0
            accelerating_days = accelerating.sum()
        else:
            accelerating_days = 0
        
        result = {
            "start_value": float(start_value),
            "end_value": float(end_value),
            "total_growth_percent": float(total_growth),
            "average_daily_growth_percent": float(avg_daily_growth),
            "growth_volatility": float(growth_volatility),
            "accelerating_growth_days": int(accelerating_days),
            "growth_status": "RAPID_GROWTH" if total_growth > 50 else "MODERATE_GROWTH" if total_growth > 20 else "SLOW_GROWTH" if total_growth > 0 else "DECLINE"
        }
        
        self.analytics_results["growth_trend"] = result
        
        self.logger.info(f"Growth trend analysis completed: {result['growth_status']}")
        
        return result
    
    def detect_high_load_periods(self) -> Dict[str, Any]:
        """
        Detect sustained high load periods.
        
        Returns:
            Dictionary with high load period analysis
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Detecting high load periods")
        
        high_load_threshold = self.config["kpi"]["pressure_thresholds"]["high_load"]
        critical_load_threshold = self.config["kpi"]["pressure_thresholds"]["critical_load"]
        
        load_col = "Total_System_Load" if "Total_System_Load" in self.df.columns else ("HHS_Care" if "HHS_Care" in self.df.columns else "HHS Care")
        
        if load_col not in self.df.columns:
            self.logger.warning(f"{load_col} column not found")
            return {"status": "SKIPPED", "reason": f"{load_col} column not found"}
        
        # Identify high and critical load days
        high_load_days = self.df[self.df[load_col] > high_load_threshold]
        critical_load_days = self.df[self.df[load_col] > critical_load_threshold]
        
        # Find continuous high load periods
        high_load_periods = self._find_continuous_periods(
            self.df[load_col] > high_load_threshold,
            self.config["data"]["date_column"]
        )
        
        critical_load_periods = self._find_continuous_periods(
            self.df[load_col] > critical_load_threshold,
            self.config["data"]["date_column"]
        )
        
        result = {
            "high_load_threshold": high_load_threshold,
            "critical_load_threshold": critical_load_threshold,
            "high_load_days": len(high_load_days),
            "critical_load_days": len(critical_load_days),
            "high_load_periods": high_load_periods,
            "critical_load_periods": critical_load_periods,
            "max_high_load_duration": max([p["duration"] for p in high_load_periods]) if high_load_periods else 0,
            "max_critical_load_duration": max([p["duration"] for p in critical_load_periods]) if critical_load_periods else 0
        }
        
        self.analytics_results["high_load_periods"] = result
        
        self.logger.info("High load period detection completed")
        
        return result
    
    def _find_continuous_periods(self, condition: pd.Series, date_col: str) -> List[Dict[str, Any]]:
        """
        Find continuous periods where condition is True.
        
        Args:
            condition: Boolean condition
            date_col: Date column name
            
        Returns:
            List of period dictionaries
        """
        periods = []
        current_period = []
        
        for idx, row in self.df.iterrows():
            if condition.iloc[idx] if isinstance(condition, pd.Series) else condition[idx]:
                current_period.append(row[date_col])
            else:
                if len(current_period) > 0:
                    periods.append({
                        "start": str(current_period[0]),
                        "end": str(current_period[-1]),
                        "duration": len(current_period)
                    })
                    current_period = []
        
        if len(current_period) > 0:
            periods.append({
                "start": str(current_period[0]),
                "end": str(current_period[-1]),
                "duration": len(current_period)
            })
        
        return periods
    
    def analyze_moving_average_signals(self) -> Dict[str, Any]:
        """
        Analyze moving average crossover signals.
        
        Returns:
            Dictionary with moving average signals
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Analyzing moving average signals")
        
        load_col = "HHS_Care" if "HHS_Care" in self.df.columns else ("HHS Care" if "HHS Care" in self.df.columns else "Total_System_Load")
        
        if load_col not in self.df.columns:
            self.logger.warning(f"{load_col} column not found")
            return {"status": "SKIPPED", "reason": f"{load_col} column not found"}
        
        ma_7_col = f"{load_col}_Rolling_Mean_7d"
        ma_14_col = f"{load_col}_Rolling_Mean_14d"
        
        if ma_7_col not in self.df.columns or ma_14_col not in self.df.columns:
            self.logger.warning("Rolling mean columns not found")
            return {"status": "SKIPPED", "reason": "Rolling mean columns not found"}
        
        # Calculate crossover signals
        self.df["MA_Crossover"] = self.df[ma_7_col] > self.df[ma_14_col]
        
        # Count crossovers
        crossovers = self.df["MA_Crossover"].diff().abs().sum() / 2
        
        # Current signal
        current_signal = "BULLISH" if self.df["MA_Crossover"].iloc[-1] else "BEARISH"
        
        # Calculate divergence
        current_divergence = self.df[ma_7_col].iloc[-1] - self.df[ma_14_col].iloc[-1]
        
        result = {
            "current_signal": current_signal,
            "crossover_count": int(crossovers),
            "current_divergence": float(current_divergence),
            "ma_7_current": float(self.df[ma_7_col].iloc[-1]),
            "ma_14_current": float(self.df[ma_14_col].iloc[-1]),
            "signal_strength": "STRONG" if abs(current_divergence) > self.df[load_col].std() else "WEAK"
        }
        
        self.analytics_results["moving_average_signals"] = result
        
        self.logger.info(f"Moving average analysis completed: {result['current_signal']}")
        
        return result
    
    def analyze_variance_patterns(self) -> Dict[str, Any]:
        """
        Analyze variance patterns in the data.
        
        Returns:
            Dictionary with variance analysis
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Analyzing variance patterns")
        
        load_col = "HHS_Care" if "HHS_Care" in self.df.columns else ("HHS Care" if "HHS Care" in self.df.columns else "Total_System_Load")
        
        if load_col not in self.df.columns:
            self.logger.warning(f"{load_col} column not found")
            return {"status": "SKIPPED", "reason": f"{load_col} column not found"}
        
        # Calculate variance at different windows
        var_7d = self.df[load_col].rolling(window=7, min_periods=1).var().mean()
        var_14d = self.df[load_col].rolling(window=14, min_periods=1).var().mean()
        
        # Overall variance
        overall_var = self.df[load_col].var()
        
        # Identify high volatility periods
        std_7d = self.df[load_col].rolling(window=7, min_periods=1).std()
        high_volatility_threshold = std_7d.mean() + std_7d.std()
        high_volatility_days = (std_7d > high_volatility_threshold).sum()
        
        result = {
            "overall_variance": float(overall_var),
            "variance_7d_avg": float(var_7d),
            "variance_14d_avg": float(var_14d),
            "high_volatility_days": int(high_volatility_days),
            "volatility_status": "HIGH" if high_volatility_days > len(self.df) * 0.2 else "MODERATE" if high_volatility_days > len(self.df) * 0.1 else "LOW"
        }
        
        self.analytics_results["variance_patterns"] = result
        
        self.logger.info(f"Variance analysis completed: {result['volatility_status']}")
        
        return result
    
    def run_all_analytics(self) -> Dict[str, Any]:
        """
        Run all healthcare analytics.
        
        Returns:
            Dictionary with all analytics results
        """
        self.logger.info("Running all healthcare analytics")
        
        results = {}
        
        results["capacity_stress"] = self.detect_capacity_stress()
        results["backlog_analysis"] = self.analyze_backlog()
        results["pressure_windows"] = self.analyze_pressure_windows()
        results["net_intake_trend"] = self.analyze_net_intake_trend()
        results["growth_trend"] = self.analyze_growth_trend()
        results["high_load_periods"] = self.detect_high_load_periods()
        results["moving_average_signals"] = self.analyze_moving_average_signals()
        results["variance_patterns"] = self.analyze_variance_patterns()
        
        # Add overall assessment
        results["overall_assessment"] = self._generate_overall_assessment(results)
        results["analytics_timestamp"] = datetime.now().isoformat()
        
        self.analytics_results = results
        
        self.logger.info("All healthcare analytics completed")
        
        return results
    
    def _generate_overall_assessment(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate overall system assessment.
        
        Args:
            results: Analytics results
            
        Returns:
            Overall assessment dictionary
        """
        # Count stress indicators
        stress_indicators = 0
        warnings = []
        
        if results.get("capacity_stress", {}).get("status") in ["HIGH_STRESS", "MODERATE_STRESS"]:
            stress_indicators += 1
            warnings.append("Capacity stress detected")
        
        if results.get("backlog_analysis", {}).get("trend_status") == "INCREASING":
            stress_indicators += 1
            warnings.append("Backlog increasing")
        
        if results.get("pressure_windows", {}).get("overall_pressure_status") in ["CRITICAL", "HIGH"]:
            stress_indicators += 1
            warnings.append("High pressure periods detected")
        
        if results.get("net_intake_trend", {}).get("status") == "HIGH_PRESSURE":
            stress_indicators += 1
            warnings.append("High net intake pressure")
        
        if results.get("growth_trend", {}).get("growth_status") == "RAPID_GROWTH":
            stress_indicators += 1
            warnings.append("Rapid growth detected")
        
        # Determine overall status
        if stress_indicators >= 4:
            overall_status = "CRITICAL"
        elif stress_indicators >= 3:
            overall_status = "HIGH"
        elif stress_indicators >= 2:
            overall_status = "MODERATE"
        elif stress_indicators >= 1:
            overall_status = "LOW_CONCERN"
        else:
            overall_status = "NORMAL"
        
        return {
            "overall_status": overall_status,
            "stress_indicators_count": stress_indicators,
            "warnings": warnings,
            "recommendation": self._generate_recommendation(overall_status)
        }
    
    def _generate_recommendation(self, status: str) -> str:
        """
        Generate recommendation based on status.
        
        Args:
            status: Overall status
            
        Returns:
            Recommendation string
        """
        recommendations = {
            "CRITICAL": "Immediate action required. Implement emergency capacity expansion measures and prioritize discharge processing.",
            "HIGH": "Significant concern. Activate contingency plans and increase discharge processing capacity.",
            "MODERATE": "Monitor closely. Prepare contingency plans and optimize resource allocation.",
            "LOW_CONCERN": "Continue monitoring. Review intake forecasting and discharge processes.",
            "NORMAL": "System operating within normal parameters. Continue standard operations."
        }
        
        return recommendations.get(status, "Monitor system status.")


def main():
    """
    Main function to run healthcare analytics pipeline.
    """
    analytics = HealthcareAnalytics()
    analytics.load_data()
    results = analytics.run_all_analytics()
    
    print("Healthcare Analytics Results:")
    print(f"Overall Status: {results['overall_assessment']['overall_status']}")
    print(f"Recommendation: {results['overall_assessment']['recommendation']}")
    print(f"Warnings: {results['overall_assessment']['warnings']}")


if __name__ == "__main__":
    main()

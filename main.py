"""
Main Entry Point

This module provides the main entry point for running the complete analytics pipeline.
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from src.logger import get_logger, setup_logger
from backend.utils import load_config, load_env, ensure_directory
from src.preprocessing import DataPreprocessor
from src.validation import DataValidator
from src.feature_engineering import FeatureEngineer
from src.kpi import KPICalculator
from backend.analytics import HealthcareAnalytics
from src.report_generator import ReportGenerator


def run_full_pipeline(config_path: str = "config.yaml"):
    """
    Run the complete analytics pipeline.
    
    Args:
        config_path: Path to configuration file
    """
    logger = setup_logger("main", log_file="logs/main.log")
    logger.info("Starting complete analytics pipeline")
    
    try:
        # Load configuration
        config = load_config(config_path)
        load_env()
        
        # Ensure all directories exist
        ensure_directory("data/raw")
        ensure_directory("data/processed")
        ensure_directory("reports")
        ensure_directory("output")
        ensure_directory("output/plots")
        ensure_directory("logs")
        
        # Step 1: Data Preprocessing
        logger.info("Step 1: Data Preprocessing")
        preprocessor = DataPreprocessor(config)
        df = preprocessor.preprocess_pipeline()
        logger.info(f"Preprocessing completed: {len(df)} rows")
        
        # Step 2: Data Validation
        logger.info("Step 2: Data Validation")
        validator = DataValidator(config)
        validator.load_data()
        validation_results = validator.run_all_validations()
        validator.save_validation_report()
        logger.info(f"Validation completed: {validation_results['overall_status']}")
        
        # Step 3: Feature Engineering
        logger.info("Step 3: Feature Engineering")
        engineer = FeatureEngineer(config)
        df = engineer.feature_engineering_pipeline()
        logger.info(f"Feature engineering completed: {len(df.columns)} columns")
        
        # Step 4: KPI Calculation
        logger.info("Step 4: KPI Calculation")
        calculator = KPICalculator(config)
        calculator.load_data()
        kpis = calculator.calculate_all_kpis()
        calculator.save_kpis()
        logger.info(f"KPI calculation completed: {len(kpis)} KPIs")
        
        # Step 5: Healthcare Analytics
        logger.info("Step 5: Healthcare Analytics")
        analytics = HealthcareAnalytics(config)
        analytics.load_data()
        analytics_results = analytics.run_all_analytics()
        logger.info(f"Analytics completed: {analytics_results['overall_assessment']['overall_status']}")
        
        # Step 6: Visualization (skipped in pipeline mode, available in dashboard)
        logger.info("Step 6: Visualization skipped (available in dashboard)")
        
        # Step 7: Report Generation
        logger.info("Step 7: Report Generation")
        generator = ReportGenerator(config)
        report_path = generator.generate_report(
            df=df,
            validation_results=validation_results,
            kpis=kpis,
            analytics_results=analytics_results
        )
        logger.info(f"Report generated: {report_path}")
        
        # Print summary
        print("\n" + "="*60)
        print("ANALYTICS PIPELINE COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"Data Rows: {len(df)}")
        print(f"Data Columns: {len(df.columns)}")
        print(f"Validation Status: {validation_results['overall_status']}")
        print(f"Overall System Status: {analytics_results['overall_assessment']['overall_status']}")
        print(f"Report Generated: {report_path}")
        print("="*60)
        
        logger.info("Pipeline completed successfully")
        
        return {
            "status": "success",
            "validation": validation_results['overall_status'],
            "system_status": analytics_results['overall_assessment']['overall_status'],
            "report_path": report_path
        }
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        print(f"\nERROR: Pipeline failed - {str(e)}")
        return {
            "status": "failed",
            "error": str(e)
        }


def run_preprocessing_only(config_path: str = "config.yaml"):
    """
    Run only the preprocessing pipeline.
    
    Args:
        config_path: Path to configuration file
    """
    logger = setup_logger("preprocessing", log_file="logs/preprocessing.log")
    logger.info("Running preprocessing pipeline")
    
    try:
        config = load_config(config_path)
        load_env()
        
        preprocessor = DataPreprocessor(config)
        df = preprocessor.preprocess_pipeline()
        
        print(f"Preprocessing completed: {len(df)} rows processed")
        return df
        
    except Exception as e:
        logger.error(f"Preprocessing failed: {str(e)}")
        print(f"ERROR: {str(e)}")
        return None


def run_validation_only(config_path: str = "config.yaml"):
    """
    Run only the validation pipeline.
    
    Args:
        config_path: Path to configuration file
    """
    logger = setup_logger("validation", log_file="logs/validation.log")
    logger.info("Running validation pipeline")
    
    try:
        config = load_config(config_path)
        load_env()
        
        validator = DataValidator(config)
        validator.load_data()
        results = validator.run_all_validations()
        validator.save_validation_report()
        
        print(validator.get_validation_summary())
        return results
        
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        print(f"ERROR: {str(e)}")
        return None


def run_analytics_only(config_path: str = "config.yaml"):
    """
    Run only the analytics pipeline.
    
    Args:
        config_path: Path to configuration file
    """
    logger = setup_logger("analytics", log_file="logs/analytics.log")
    logger.info("Running analytics pipeline")
    
    try:
        config = load_config(config_path)
        load_env()
        
        analytics = HealthcareAnalytics(config)
        analytics.load_data()
        results = analytics.run_all_analytics()
        
        print(f"Overall Status: {results['overall_assessment']['overall_status']}")
        print(f"Recommendation: {results['overall_assessment']['recommendation']}")
        return results
        
    except Exception as e:
        logger.error(f"Analytics failed: {str(e)}")
        print(f"ERROR: {str(e)}")
        return None


def main():
    """
    Main function with command-line interface.
    """
    parser = argparse.ArgumentParser(
        description="System Capacity & Care Load Analytics"
    )
    
    parser.add_argument(
        "--mode",
        type=str,
        default="full",
        choices=["full", "preprocessing", "validation", "analytics"],
        help="Pipeline mode to run"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file"
    )
    
    args = parser.parse_args()
    
    if args.mode == "full":
        run_full_pipeline(args.config)
    elif args.mode == "preprocessing":
        run_preprocessing_only(args.config)
    elif args.mode == "validation":
        run_validation_only(args.config)
    elif args.mode == "analytics":
        run_analytics_only(args.config)


if __name__ == "__main__":
    main()

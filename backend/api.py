"""
FastAPI Backend Module

This module provides REST API endpoints for the healthcare analytics system.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from pathlib import Path
import sys
import uvicorn

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.logger import get_logger
from backend.utils import load_config, load_env
from backend.analytics import HealthcareAnalytics
from src.kpi import KPICalculator
from src.preprocessing import DataPreprocessor
from src.validation import DataValidator
from src.feature_engineering import FeatureEngineer
from src.report_generator import ReportGenerator


# Pydantic models for request/response
class PipelineResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None


class KPIResponse(BaseModel):
    kpis: Dict[str, Any]
    timestamp: str


class AnalyticsResponse(BaseModel):
    analytics: Dict[str, Any]
    timestamp: str


class SummaryResponse(BaseModel):
    kpis: Dict[str, Any]
    analytics: Dict[str, Any]
    overall_status: str
    timestamp: str


# Initialize FastAPI app
app = FastAPI(
    title="System Capacity & Care Load Analytics API",
    description="REST API for HHS Unaccompanied Alien Children Program Analytics",
    version="1.0.0"
)

# Load configuration
config = load_config()
logger = get_logger(__name__)

# Global variables for cached data
cached_kpis: Optional[Dict[str, Any]] = None
cached_analytics: Optional[Dict[str, Any]] = None
cached_data: Optional[Any] = None


@app.on_event("startup")
async def startup_event():
    """Initialize data on startup."""
    logger.info("Starting FastAPI backend")
    load_env()
    
    # Run initial data processing
    try:
        preprocessor = DataPreprocessor(config)
        preprocessor.preprocess_pipeline()
        
        validator = DataValidator(config)
        validator.load_data()
        validator.run_all_validations()
        
        engineer = FeatureEngineer(config)
        engineer.feature_engineering_pipeline()
        
        # Cache initial KPIs and analytics
        calculator = KPICalculator(config)
        calculator.load_data()
        global cached_kpis
        cached_kpis = calculator.calculate_all_kpis()
        
        analytics = HealthcareAnalytics(config)
        analytics.load_data()
        global cached_analytics
        cached_analytics = analytics.run_all_analytics()
        
        logger.info("Backend initialized successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")


@app.get("/", response_model=PipelineResponse)
async def root():
    """Root endpoint."""
    return PipelineResponse(
        status="success",
        message="System Capacity & Care Load Analytics API",
        data={"version": "1.0.0"}
    )


@app.get("/health", response_model=PipelineResponse)
async def health_check():
    """Health check endpoint."""
    return PipelineResponse(
        status="healthy",
        message="Service is running",
        data={"cached_data": cached_kpis is not None}
    )


@app.post("/refresh", response_model=PipelineResponse)
async def refresh_data(background_tasks: BackgroundTasks):
    """
    Refresh data and recalculate KPIs and analytics.
    
    This endpoint triggers a background task to reprocess data and update cached results.
    """
    def refresh_task():
        try:
            logger.info("Starting data refresh")
            
            # Reprocess data
            preprocessor = DataPreprocessor(config)
            preprocessor.preprocess_pipeline()
            
            validator = DataValidator(config)
            validator.load_data()
            validator.run_all_validations()
            
            engineer = FeatureEngineer(config)
            engineer.feature_engineering_pipeline()
            
            # Recalculate KPIs
            calculator = KPICalculator(config)
            calculator.load_data()
            global cached_kpis
            cached_kpis = calculator.calculate_all_kpis()
            
            # Recalculate analytics
            analytics = HealthcareAnalytics(config)
            analytics.load_data()
            global cached_analytics
            cached_analytics = analytics.run_all_analytics()
            
            logger.info("Data refresh completed successfully")
            
        except Exception as e:
            logger.error(f"Error during data refresh: {str(e)}")
    
    background_tasks.add_task(refresh_task)
    
    return PipelineResponse(
        status="success",
        message="Data refresh initiated"
    )


@app.get("/kpis", response_model=KPIResponse)
async def get_kpis():
    """
    Get current KPIs.
    
    Returns calculated Key Performance Indicators for the system.
    """
    if cached_kpis is None:
        raise HTTPException(status_code=503, detail="KPIs not available. Data not processed yet.")
    
    return KPIResponse(
        kpis=cached_kpis,
        timestamp=cached_kpis.get("calculation_timestamp", "")
    )


@app.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    """
    Get healthcare analytics results.
    
    Returns comprehensive analytics including capacity stress, backlog analysis, 
    pressure windows, and growth trends.
    """
    if cached_analytics is None:
        raise HTTPException(status_code=503, detail="Analytics not available. Data not processed yet.")
    
    return AnalyticsResponse(
        analytics=cached_analytics,
        timestamp=cached_analytics.get("analytics_timestamp", "")
    )


@app.get("/capacity", response_model=PipelineResponse)
async def get_capacity():
    """
    Get capacity analysis.
    
    Returns capacity stress detection and load analysis.
    """
    if cached_analytics is None:
        raise HTTPException(status_code=503, detail="Analytics not available.")
    
    capacity_data = {
        "capacity_stress": cached_analytics.get("capacity_stress", {}),
        "high_load_periods": cached_analytics.get("high_load_periods", {}),
        "moving_average_signals": cached_analytics.get("moving_average_signals", {})
    }
    
    return PipelineResponse(
        status="success",
        message="Capacity analysis retrieved",
        data=capacity_data
    )


@app.get("/trends", response_model=PipelineResponse)
async def get_trends():
    """
    Get trend analysis.
    
    Returns net intake trends and growth patterns.
    """
    if cached_analytics is None:
        raise HTTPException(status_code=503, detail="Analytics not available.")
    
    trends_data = {
        "net_intake_trend": cached_analytics.get("net_intake_trend", {}),
        "growth_trend": cached_analytics.get("growth_trend", {}),
        "variance_patterns": cached_analytics.get("variance_patterns", {})
    }
    
    return PipelineResponse(
        status="success",
        message="Trend analysis retrieved",
        data=trends_data
    )


@app.get("/backlog", response_model=PipelineResponse)
async def get_backlog():
    """
    Get backlog analysis.
    
    Returns backlog accumulation and trend analysis.
    """
    if cached_analytics is None:
        raise HTTPException(status_code=503, detail="Analytics not available.")
    
    backlog_data = {
        "backlog_analysis": cached_analytics.get("backlog_analysis", {}),
        "pressure_windows": cached_analytics.get("pressure_windows", {})
    }
    
    return PipelineResponse(
        status="success",
        message="Backlog analysis retrieved",
        data=backlog_data
    )


@app.get("/summary", response_model=SummaryResponse)
async def get_summary():
    """
    Get comprehensive summary.
    
    Returns KPIs, analytics, and overall system status.
    """
    if cached_kpis is None or cached_analytics is None:
        raise HTTPException(status_code=503, detail="Data not processed yet.")
    
    overall_status = cached_analytics.get("overall_assessment", {}).get("overall_status", "UNKNOWN")
    
    return SummaryResponse(
        kpis=cached_kpis,
        analytics=cached_analytics,
        overall_status=overall_status,
        timestamp=cached_analytics.get("analytics_timestamp", "")
    )


@app.get("/validation", response_model=PipelineResponse)
async def get_validation():
    """
    Get data validation results.
    
    Returns results from automated data validation checks.
    """
    try:
        validator = DataValidator(config)
        validator.load_data()
        results = validator.run_all_validations()
        
        return PipelineResponse(
            status="success",
            message="Validation results retrieved",
            data=results
        )
        
    except Exception as e:
        logger.error(f"Error getting validation results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/report/generate")
async def generate_report(background_tasks: BackgroundTasks):
    """
    Generate PDF report.
    
    Triggers background task to generate comprehensive PDF report.
    """
    def generate_report_task():
        try:
            logger.info("Starting PDF report generation")
            
            # Load data
            import pandas as pd
            df = pd.read_csv("data/processed/featured_data.csv")
            
            # Get validation results
            validator = DataValidator(config)
            validator.load_data()
            validation_results = validator.run_all_validations()
            
            # Get KPIs
            calculator = KPICalculator(config)
            calculator.load_data()
            kpis = calculator.calculate_all_kpis()
            
            # Get analytics
            analytics = HealthcareAnalytics(config)
            analytics.load_data()
            analytics_results = analytics.run_all_analytics()
            
            # Generate report
            generator = ReportGenerator(config)
            report_path = generator.generate_report(
                df=df,
                validation_results=validation_results,
                kpis=kpis,
                analytics_results=analytics_results
            )
            
            logger.info(f"PDF report generated: {report_path}")
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
    
    background_tasks.add_task(generate_report_task)
    
    return PipelineResponse(
        status="success",
        message="Report generation initiated"
    )


@app.get("/report/download")
async def download_report():
    """
    Download the latest generated PDF report.
    """
    reports_dir = Path("reports")
    
    # Find the most recent PDF report
    pdf_files = list(reports_dir.glob("*.pdf"))
    
    if not pdf_files:
        raise HTTPException(status_code=404, detail="No report found. Generate a report first.")
    
    # Get the most recent file
    latest_report = max(pdf_files, key=lambda p: p.stat().st_mtime)
    
    return FileResponse(
        path=str(latest_report),
        media_type="application/pdf",
        filename=latest_report.name
    )


@app.get("/export/csv")
async def export_csv():
    """
    Export processed data as CSV.
    """
    try:
        data_path = Path("data/processed/featured_data.csv")
        
        if not data_path.exists():
            raise HTTPException(status_code=404, detail="Processed data not found.")
        
        return FileResponse(
            path=str(data_path),
            media_type="text/csv",
            filename="featured_data.csv"
        )
        
    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/export/excel")
async def export_excel():
    """
    Export processed data as Excel.
    """
    try:
        import pandas as pd
        
        data_path = Path("data/processed/featured_data.csv")
        
        if not data_path.exists():
            raise HTTPException(status_code=404, detail="Processed data not found.")
        
        # Read CSV and convert to Excel
        df = pd.read_csv(data_path)
        excel_path = Path("output/featured_data.xlsx")
        excel_path.parent.mkdir(exist_ok=True)
        
        df.to_excel(excel_path, index=False, engine='openpyxl')
        
        return FileResponse(
            path=str(excel_path),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="featured_data.xlsx"
        )
        
    except Exception as e:
        logger.error(f"Error exporting Excel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def start_server():
    """
    Start the FastAPI server.
    """
    host = config["api"]["host"]
    port = config["api"]["port"]
    reload = config["api"]["reload"]
    log_level = config["api"]["log_level"]
    
    logger.info(f"Starting FastAPI server on {host}:{port}")
    
    uvicorn.run(
        "backend.api:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )


if __name__ == "__main__":
    start_server()

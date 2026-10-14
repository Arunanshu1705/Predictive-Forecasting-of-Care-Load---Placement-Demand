"""
Streamlit Main Application

This is the main entry point for the Streamlit dashboard.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.logger import get_logger
from backend.utils import load_config, load_env
from src.preprocessing import DataPreprocessor
from src.validation import DataValidator
from src.feature_engineering import FeatureEngineer
from src.kpi import KPICalculator
from src.visualization import Visualizer
from backend.analytics import HealthcareAnalytics
from src.report_generator import ReportGenerator

# Page configuration
st.set_page_config(
    page_title="System Capacity & Care Load Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load configuration
config = load_config()
load_env()
logger = get_logger(__name__)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-normal {
        color: #2ca02c;
        font-weight: bold;
    }
    .status-warning {
        color: #ff7f0e;
        font-weight: bold;
    }
    .status-critical {
        color: #d62728;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def process_data():
    """
    Process data pipeline.
    
    Returns:
        Tuple of (df, kpis, analytics_results)
    """
    with st.spinner("Processing data..."):
        try:
            # Preprocessing
            preprocessor = DataPreprocessor(config)
            preprocessor.preprocess_pipeline()
            
            # Validation
            validator = DataValidator(config)
            validator.load_data()
            validation_results = validator.run_all_validations()
            
            # Feature Engineering
            engineer = FeatureEngineer(config)
            df = engineer.feature_engineering_pipeline()
            
            # KPI Calculation
            calculator = KPICalculator(config)
            calculator.load_data()
            kpis = calculator.calculate_all_kpis()
            
            # Analytics
            analytics = HealthcareAnalytics(config)
            analytics.load_data()
            analytics_results = analytics.run_all_analytics()
            
            return df, kpis, analytics_results, validation_results
            
        except Exception as e:
            st.error(f"Error processing data: {str(e)}")
            logger.error(f"Error processing data: {str(e)}")
            return None, None, None, None


def load_cached_data():
    """
    Load cached data if available.
    
    Returns:
        Tuple of (df, kpis, analytics_results)
    """
    try:
        df = pd.read_csv("data/processed/featured_data.csv")
        
        calculator = KPICalculator(config)
        calculator.load_data()
        kpis = calculator.calculate_all_kpis()
        
        analytics = HealthcareAnalytics(config)
        analytics.load_data()
        analytics_results = analytics.run_all_analytics()
        
        return df, kpis, analytics_results
        
    except Exception as e:
        logger.warning(f"Could not load cached data: {str(e)}")
        return None, None, None


def main():
    """
    Main application function.
    """
    # Title
    st.markdown('<h1 class="main-title">System Capacity & Care Load Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">HHS Unaccompanied Alien Children Program</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    
    # Data processing button
    st.sidebar.header("Data Processing")
    process_button = st.sidebar.button("Process/Refresh Data", type="primary")
    
    # Initialize session state
    if "df" not in st.session_state:
        st.session_state.df = None
    if "kpis" not in st.session_state:
        st.session_state.kpis = None
    if "analytics" not in st.session_state:
        st.session_state.analytics = None
    if "validation" not in st.session_state:
        st.session_state.validation = None
    
    # Process data if button clicked or no data in session
    if process_button or st.session_state.df is None:
        df, kpis, analytics, validation = process_data()
        
        if df is not None:
            st.session_state.df = df
            st.session_state.kpis = kpis
            st.session_state.analytics = analytics
            st.session_state.validation = validation
            st.success("Data processed successfully!")
        else:
            st.error("Failed to process data. Please check the data file.")
            return
    
    # Display overall status in sidebar
    if st.session_state.analytics:
        overall_status = st.session_state.analytics.get("overall_assessment", {}).get("overall_status", "UNKNOWN")
        status_color = {
            "NORMAL": "status-normal",
            "LOW_CONCERN": "status-normal",
            "MODERATE": "status-warning",
            "HIGH": "status-warning",
            "CRITICAL": "status-critical"
        }.get(overall_status, "")
        
        st.sidebar.markdown(f"**System Status:**")
        st.sidebar.markdown(f'<p class="{status_color}">{overall_status}</p>', unsafe_allow_html=True)
        
        recommendation = st.session_state.analytics.get("overall_assessment", {}).get("recommendation", "")
        if recommendation:
            st.sidebar.info(f"**Recommendation:**\n{recommendation}")
    
    # Data info in sidebar
    if st.session_state.df is not None:
        st.sidebar.header("Data Information")
        st.sidebar.metric("Total Records", len(st.session_state.df))
        
        date_col = config["data"]["date_column"]
        if date_col in st.session_state.df.columns:
            st.session_state.df[date_col] = pd.to_datetime(st.session_state.df[date_col])
            st.sidebar.metric("Date Range Start", str(st.session_state.df[date_col].min().date()))
            st.sidebar.metric("Date Range End", str(st.session_state.df[date_col].max().date()))
    
    # Export options
    st.sidebar.header("Export Options")
    
    if st.sidebar.button("Generate PDF Report"):
        with st.spinner("Generating report..."):
            try:
                generator = ReportGenerator(config)
                report_path = generator.generate_simple_report(
                    kpis=st.session_state.kpis,
                    analytics_results=st.session_state.analytics
                )
                st.success(f"Report generated: {report_path}")
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")
    
    if st.sidebar.button("Export to CSV"):
        try:
            csv_path = "output/exported_data.csv"
            st.session_state.df.to_csv(csv_path, index=False)
            st.success(f"Data exported to: {csv_path}")
        except Exception as e:
            st.error(f"Error exporting CSV: {str(e)}")
    
    if st.sidebar.button("Export to Excel"):
        try:
            excel_path = "output/exported_data.xlsx"
            st.session_state.df.to_excel(excel_path, index=False, engine='openpyxl')
            st.success(f"Data exported to: {excel_path}")
        except Exception as e:
            st.error(f"Error exporting Excel: {str(e)}")
    
    # Page navigation
    st.sidebar.header("Pages")
    page = st.sidebar.radio(
        "Select a page:",
        ["Overview", "Capacity", "Trends", "Pressure Analysis", "KPIs", "Insights"]
    )
    
    # Render selected page
    if page == "Overview":
        from page_modules.overview import show_overview
        show_overview(st.session_state.df, st.session_state.kpis, st.session_state.analytics)
    
    elif page == "Capacity":
        from page_modules.capacity import show_capacity
        show_capacity(st.session_state.df, st.session_state.analytics)
    
    elif page == "Trends":
        from page_modules.trends import show_trends
        show_trends(st.session_state.df, st.session_state.analytics)
    
    elif page == "Pressure Analysis":
        from page_modules.backlog import show_pressure_analysis
        show_pressure_analysis(st.session_state.df, st.session_state.analytics)
    
    elif page == "KPIs":
        from page_modules.kpis import show_kpis
        show_kpis(st.session_state.kpis)
    
    elif page == "Insights":
        from page_modules.insights import show_insights
        show_insights(st.session_state.analytics, st.session_state.validation)


if __name__ == "__main__":
    main()

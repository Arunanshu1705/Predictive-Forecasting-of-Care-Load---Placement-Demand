"""
Report Generator Module

This module generates comprehensive PDF reports for the analytics project.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.logger import get_logger
from backend.utils import load_config, ensure_directory

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
    print("ReportLab not installed. Install with: pip install reportlab")
    raise


class ReportGenerator:
    """
    Report generator class for HHS UAC Program analytics.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the ReportGenerator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or load_config()
        self.logger = get_logger(__name__)
        self.doc: Optional[SimpleDocTemplate] = None
        self.story: List = []
        self.styles: Optional[Dict[str, Any]] = None
        
    def setup_document(self, output_path: Optional[str] = None) -> None:
        """
        Setup the PDF document.
        
        Args:
            output_path: Output file path
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"reports/capacity_analytics_report_{timestamp}.pdf"
        
        self.logger.info(f"Setting up PDF document: {output_path}")
        
        # Ensure output directory exists
        output_file = Path(output_path)
        ensure_directory(str(output_file.parent))
        
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Setup styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        self.story = []
    
    def _setup_custom_styles(self) -> None:
        """
        Setup custom paragraph styles.
        """
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2ca02c'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Normal style
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            leading=14
        ))
        
        # Table header style
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.white,
            alignment=TA_CENTER
        ))
    
    def add_title(self, title: str) -> None:
        """
        Add title to the report.
        
        Args:
            title: Title text
        """
        self.story.append(Paragraph(title, self.styles['CustomTitle']))
        self.story.append(Spacer(1, 0.2 * inch))
    
    def add_subtitle(self, subtitle: str) -> None:
        """
        Add subtitle to the report.
        
        Args:
            subtitle: Subtitle text
        """
        self.story.append(Paragraph(subtitle, self.styles['CustomSubtitle']))
        self.story.append(Spacer(1, 0.1 * inch))
    
    def add_paragraph(self, text: str) -> None:
        """
        Add paragraph to the report.
        
        Args:
            text: Paragraph text
        """
        self.story.append(Paragraph(text, self.styles['CustomNormal']))
        self.story.append(Spacer(1, 0.1 * inch))
    
    def add_table(self, data: List[List[str]], headers: List[str], 
                  col_widths: Optional[List[float]] = None) -> None:
        """
        Add table to the report.
        
        Args:
            data: Table data (list of lists)
            headers: Table headers
            col_widths: Column widths (optional)
        """
        # Create table with headers
        table_data = [headers] + data
        
        if col_widths is None:
            col_widths = [len(str(h)) * 0.1 * inch for h in headers]
        
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Style the table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.2 * inch))
    
    def add_kpi_table(self, kpis: Dict[str, Any]) -> None:
        """
        Add KPI table to the report.
        
        Args:
            kpis: KPI dictionary
        """
        self.add_subtitle("Key Performance Indicators")
        
        kpi_data = []
        for key, value in kpis.items():
            if key in ["calculation_timestamp", "data_period"]:
                continue
            if isinstance(value, dict):
                continue
            kpi_data.append([key.replace("_", " ").title(), str(value)])
        
        self.add_table(kpi_data, ["KPI", "Value"])
    
    def add_validation_summary(self, validation_results: Dict[str, Any]) -> None:
        """
        Add validation summary to the report.
        
        Args:
            validation_results: Validation results dictionary
        """
        self.add_subtitle("Data Validation Summary")
        
        # Overall status
        overall_status = validation_results.get("overall_status", "N/A")
        self.add_paragraph(f"Overall Validation Status: <b>{overall_status}</b>")
        
        # Failed checks
        failed_checks = validation_results.get("failed_checks", [])
        if failed_checks:
            self.add_paragraph("<b>Failed Checks:</b>")
            for check in failed_checks:
                self.add_paragraph(f"  - {check}")
        
        # Warning checks
        warning_checks = validation_results.get("warning_checks", [])
        if warning_checks:
            self.add_paragraph("<b>Warning Checks:</b>")
            for check in warning_checks:
                self.add_paragraph(f"  - {check}")
        
        self.story.append(Spacer(1, 0.2 * inch))
    
    def add_analytics_summary(self, analytics_results: Dict[str, Any]) -> None:
        """
        Add analytics summary to the report.
        
        Args:
            analytics_results: Analytics results dictionary
        """
        self.add_subtitle("Healthcare Analytics Summary")
        
        # Overall assessment
        overall = analytics_results.get("overall_assessment", {})
        self.add_paragraph(f"Overall System Status: <b>{overall.get('overall_status', 'N/A')}</b>")
        self.add_paragraph(f"Recommendation: {overall.get('recommendation', 'N/A')}")
        
        # Warnings
        warnings = overall.get("warnings", [])
        if warnings:
            self.add_paragraph("<b>Warnings:</b>")
            for warning in warnings:
                self.add_paragraph(f"  - {warning}")
        
        self.story.append(Spacer(1, 0.2 * inch))
        
        # Key analytics
        self.add_subtitle("Key Analytics Results")
        
        analytics_data = []
        
        # Capacity stress
        capacity_stress = analytics_results.get("capacity_stress", {})
        if capacity_stress.get("status") != "SKIPPED":
            analytics_data.append([
                "Capacity Stress Status",
                capacity_stress.get("status", "N/A")
            ])
            analytics_data.append([
                "Stress Days",
                str(capacity_stress.get("stress_days", 0))
            ])
        
        # Backlog analysis
        backlog = analytics_results.get("backlog_analysis", {})
        if backlog.get("status") != "SKIPPED":
            analytics_data.append([
                "Backlog Trend",
                backlog.get("trend_status", "N/A")
            ])
            analytics_data.append([
                "Current Backlog",
                f"{backlog.get('current_backlog', 0):.0f}"
            ])
        
        # Net intake trend
        net_intake = analytics_results.get("net_intake_trend", {})
        if net_intake.get("status") != "SKIPPED":
            analytics_data.append([
                "Net Intake Trend",
                net_intake.get("trend_direction", "N/A")
            ])
        
        # Growth trend
        growth = analytics_results.get("growth_trend", {})
        if growth.get("status") != "SKIPPED":
            analytics_data.append([
                "Growth Status",
                growth.get("growth_status", "N/A")
            ])
            analytics_data.append([
                "Total Growth %",
                f"{growth.get('total_growth_percent', 0):.1f}%"
            ])
        
        if analytics_data:
            self.add_table(analytics_data, ["Metric", "Value"])
    
    def add_dataset_overview(self, df: pd.DataFrame) -> None:
        """
        Add dataset overview to the report.
        
        Args:
            df: DataFrame
        """
        self.add_subtitle("Dataset Overview")
        
        date_col = self.config["data"]["date_column"]
        
        # Basic statistics
        overview_data = [
            ["Total Records", str(len(df))],
            ["Date Range Start", str(df[date_col].min())],
            ["Date Range End", str(df[date_col].max())],
            ["Total Columns", str(len(df.columns))]
        ]
        
        self.add_table(overview_data, ["Metric", "Value"])
        
        # Column information
        self.add_subtitle("Data Columns")
        col_data = [[col, str(df[col].dtype)] for col in df.columns]
        self.add_table(col_data, ["Column", "Data Type"])
    
    def add_recommendations(self, analytics_results: Dict[str, Any]) -> None:
        """
        Add recommendations section to the report.
        
        Args:
            analytics_results: Analytics results dictionary
        """
        self.add_subtitle("Recommendations")
        
        overall = analytics_results.get("overall_assessment", {})
        recommendation = overall.get("recommendation", "No specific recommendations available.")
        
        self.add_paragraph(recommendation)
        
        # Add specific recommendations based on analysis
        recommendations_list = []
        
        capacity_stress = analytics_results.get("capacity_stress", {})
        if capacity_stress.get("status") == "HIGH_STRESS":
            recommendations_list.append(
                "Implement immediate capacity expansion measures and consider temporary overflow facilities."
            )
        
        backlog = analytics_results.get("backlog_analysis", {})
        if backlog.get("trend_status") == "INCREASING":
            recommendations_list.append(
                "Increase discharge processing capacity and review placement procedures to reduce backlog accumulation."
            )
        
        pressure = analytics_results.get("pressure_windows", {})
        if pressure.get("overall_pressure_status") in ["CRITICAL", "HIGH"]:
            recommendations_list.append(
                "Activate contingency protocols and allocate additional resources for high-pressure periods."
            )
        
        growth = analytics_results.get("growth_trend", {})
        if growth.get("growth_status") == "RAPID_GROWTH":
            recommendations_list.append(
                "Review intake forecasting models and ensure adequate staffing levels for projected growth."
            )
        
        if recommendations_list:
            self.add_paragraph("<b>Specific Actions:</b>")
            for i, rec in enumerate(recommendations_list, 1):
                self.add_paragraph(f"{i}. {rec}")
    
    def add_conclusion(self, analytics_results: Dict[str, Any]) -> None:
        """
        Add conclusion section to the report.
        
        Args:
            analytics_results: Analytics results dictionary
        """
        self.add_subtitle("Conclusion")
        
        overall = analytics_results.get("overall_assessment", {})
        status = overall.get("overall_status", "N/A")
        
        conclusion_text = f"""
        This report provides a comprehensive analysis of the HHS Unaccompanied Alien Children 
        Program capacity and care load metrics. The current system status is <b>{status}</b>.
        
        The analysis includes data validation, feature engineering, KPI calculations, and 
        specialized healthcare analytics covering capacity stress, backlog trends, pressure 
        windows, and growth patterns.
        
        Continuous monitoring and regular analysis of these metrics will help ensure optimal 
        system performance and enable proactive response to capacity challenges.
        """
        
        self.add_paragraph(conclusion_text)
    
    def add_page_break(self) -> None:
        """Add page break to the report."""
        self.story.append(PageBreak())
    
    def generate_report(self, 
                       df: pd.DataFrame,
                       validation_results: Dict[str, Any],
                       kpis: Dict[str, Any],
                       analytics_results: Dict[str, Any],
                       output_path: Optional[str] = None) -> str:
        """
        Generate complete PDF report.
        
        Args:
            df: DataFrame
            validation_results: Validation results
            kpis: KPI results
            analytics_results: Analytics results
            output_path: Output file path
            
        Returns:
            Path to generated report
        """
        self.logger.info("Generating PDF report")
        
        # Setup document
        self.setup_document(output_path)
        
        # Title page
        self.add_title("System Capacity & Care Load Analytics")
        self.add_subtitle("HHS Unaccompanied Alien Children Program")
        self.add_paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.add_page_break()
        
        # Executive Summary
        self.add_subtitle("Executive Summary")
        overall = analytics_results.get("overall_assessment", {})
        self.add_paragraph(f"Overall System Status: <b>{overall.get('overall_status', 'N/A')}</b>")
        self.add_paragraph(overall.get("recommendation", "No specific recommendations available."))
        self.add_page_break()
        
        # Dataset Overview
        self.add_subtitle("Dataset Overview")
        self.add_dataset_overview(df)
        self.add_page_break()
        
        # Validation Report
        self.add_subtitle("Data Validation Report")
        self.add_validation_summary(validation_results)
        self.add_page_break()
        
        # KPIs
        self.add_kpi_table(kpis)
        self.add_page_break()
        
        # Analytics Summary
        self.add_analytics_summary(analytics_results)
        self.add_page_break()
        
        # Recommendations
        self.add_recommendations(analytics_results)
        self.add_page_break()
        
        # Conclusion
        self.add_conclusion(analytics_results)
        
        # Build the PDF
        self.doc.build(self.story)
        
        self.logger.info("PDF report generated successfully")
        
        return self.doc.filename
    
    def generate_simple_report(self, 
                              kpis: Dict[str, Any],
                              analytics_results: Dict[str, Any],
                              output_path: Optional[str] = None) -> str:
        """
        Generate simplified PDF report with key findings.
        
        Args:
            kpis: KPI results
            analytics_results: Analytics results
            output_path: Output file path
            
        Returns:
            Path to generated report
        """
        self.logger.info("Generating simplified PDF report")
        
        # Setup document
        self.setup_document(output_path)
        
        # Title
        self.add_title("System Capacity & Care Load Analytics")
        self.add_subtitle("Executive Summary Report")
        self.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Overall Status
        overall = analytics_results.get("overall_assessment", {})
        self.add_subtitle("Overall System Status")
        self.add_paragraph(f"Status: <b>{overall.get('overall_status', 'N/A')}</b>")
        self.add_paragraph(f"Recommendation: {overall.get('recommendation', 'N/A')}")
        
        # Key KPIs
        self.add_kpi_table(kpis)
        
        # Key Analytics
        self.add_analytics_summary(analytics_results)
        
        # Recommendations
        self.add_recommendations(analytics_results)
        
        # Build the PDF
        self.doc.build(self.story)
        
        self.logger.info("Simplified PDF report generated successfully")
        
        return self.doc.filename


def main():
    """
    Main function to test report generation.
    """
    # This would be called with actual data in production
    generator = ReportGenerator()
    
    # Sample data for testing
    sample_kpis = {
        "total_children_under_care": 10000,
        "average_daily_intake": 500,
        "average_daily_discharges": 450,
        "calculation_timestamp": datetime.now().isoformat()
    }
    
    sample_analytics = {
        "overall_assessment": {
            "overall_status": "MODERATE",
            "recommendation": "Monitor closely and prepare contingency plans.",
            "warnings": ["Backlog increasing"]
        }
    }
    
    sample_validation = {
        "overall_status": "PASS",
        "failed_checks": [],
        "warning_checks": []
    }
    
    # Generate simple report
    report_path = generator.generate_simple_report(
        sample_kpis,
        sample_analytics
    )
    
    print(f"Report generated: {report_path}")


if __name__ == "__main__":
    main()

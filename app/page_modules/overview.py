"""
Overview Page

Displays system overview with key metrics and summary information.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime


def show_overview(df, kpis, analytics):
    """
    Display overview page.
    
    Args:
        df: DataFrame with processed data
        kpis: KPI dictionary
        analytics: Analytics results dictionary
    """
    st.header("System Overview")
    
    if kpis is None or analytics is None:
        st.warning("No data available. Please process data first.")
        return
    
    # Overall status
    st.subheader("System Status")
    
    overall_assessment = analytics.get("overall_assessment", {})
    overall_status = overall_assessment.get("overall_status", "UNKNOWN")
    
    status_colors = {
        "NORMAL": "🟢",
        "LOW_CONCERN": "🟢",
        "MODERATE": "🟡",
        "HIGH": "🟠",
        "CRITICAL": "🔴"
    }
    
    status_emoji = status_colors.get(overall_status, "⚪")
    st.markdown(f"### {status_emoji} Overall System Status: {overall_status}")
    
    recommendation = overall_assessment.get("recommendation", "")
    if recommendation:
        st.info(f"**Recommendation:** {recommendation}")
    
    # Warnings
    warnings = overall_assessment.get("warnings", [])
    if warnings:
        st.warning("**Active Warnings:**")
        for warning in warnings:
            st.markdown(f"• {warning}")
    
    st.markdown("---")
    
    # Key KPI Cards
    st.subheader("Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_children = kpis.get("total_children_under_care", 0)
        st.metric(
            "Total Children Under Care",
            f"{total_children:,.0f}",
            delta="Current"
        )
    
    with col2:
        avg_daily_intake = kpis.get("average_daily_intake", 0)
        st.metric(
            "Average Daily Intake",
            f"{avg_daily_intake:,.0f}",
            delta="Daily Average"
        )
    
    with col3:
        avg_daily_discharges = kpis.get("average_daily_discharges", 0)
        st.metric(
            "Average Daily Discharges",
            f"{avg_daily_discharges:,.0f}",
            delta="Daily Average"
        )
    
    with col4:
        net_intake_pressure = kpis.get("net_intake_pressure", 0)
        delta_color = "normal" if net_intake_pressure > 0 else "inverse"
        st.metric(
            "Net Intake Pressure",
            f"{net_intake_pressure:,.0f}",
            delta=f"{net_intake_pressure:+,.0f}",
            delta_color=delta_color
        )
    
    st.markdown("---")
    
    # Secondary KPIs
    st.subheader("Additional Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_system_load = kpis.get("average_system_load", 0)
        st.metric(
            "Average System Load",
            f"{avg_system_load:,.0f}",
            delta="Overall Average"
        )
    
    with col2:
        volatility_index = kpis.get("care_load_volatility_index", 0)
        st.metric(
            "Volatility Index",
            f"{volatility_index:.3f}",
            delta="Stability Measure"
        )
    
    with col3:
        discharge_ratio = kpis.get("discharge_offset_ratio", 0)
        st.metric(
            "Discharge Offset Ratio",
            f"{discharge_ratio:.3f}",
            delta="Ratio"
        )
    
    with col4:
        backlog_rate = kpis.get("backlog_accumulation_rate", 0)
        st.metric(
            "Backlog Accumulation Rate",
            f"{backlog_rate:,.0f}/day",
            delta="Daily Change"
        )
    
    st.markdown("---")
    
    # Extreme Values
    st.subheader("Extreme Values")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Peak Load Day**")
        peak = kpis.get("peak_load_day", {})
        st.markdown(f"- Date: {peak.get('date', 'N/A')}")
        st.markdown(f"- Value: {peak.get('value', 0):,.0f}")
        
        st.markdown("**Highest Intake**")
        highest_intake = kpis.get("highest_intake", {})
        st.markdown(f"- Date: {highest_intake.get('date', 'N/A')}")
        st.markdown(f"- Value: {highest_intake.get('value', 0):,.0f}")
    
    with col2:
        st.markdown("**Lowest Load Day**")
        lowest = kpis.get("lowest_load_day", {})
        st.markdown(f"- Date: {lowest.get('date', 'N/A')}")
        st.markdown(f"- Value: {lowest.get('value', 0):,.0f}")
        
        st.markdown("**Highest Discharge**")
        highest_discharge = kpis.get("highest_discharge", {})
        st.markdown(f"- Date: {highest_discharge.get('date', 'N/A')}")
        st.markdown(f"- Value: {highest_discharge.get('value', 0):,.0f}")
    
    st.markdown("---")
    
    # Quick Analytics Summary
    st.subheader("Analytics Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        capacity_stress = analytics.get("capacity_stress", {})
        stress_status = capacity_stress.get("status", "N/A")
        stress_days = capacity_stress.get("stress_days", 0)
        st.info(f"**Capacity Stress:** {stress_status}\nStress Days: {stress_days}")
    
    with col2:
        backlog = analytics.get("backlog_analysis", {})
        backlog_trend = backlog.get("trend_status", "N/A")
        current_backlog = backlog.get("current_backlog", 0)
        st.info(f"**Backlog Trend:** {backlog_trend}\nCurrent: {current_backlog:,.0f}")
    
    with col3:
        growth = analytics.get("growth_trend", {})
        growth_status = growth.get("growth_status", "N/A")
        total_growth = growth.get("total_growth_percent", 0)
        st.info(f"**Growth Status:** {growth_status}\nTotal Growth: {total_growth:.1f}%")
    
    st.markdown("---")
    
    # Recent Data Preview
    st.subheader("Recent Data")
    
    if df is not None:
        date_col = "Date"
        if date_col in df.columns:
            df_sorted = df.sort_values(by=date_col, ascending=False)
            st.dataframe(
                df_sorted.head(10),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.warning("No data available for preview")

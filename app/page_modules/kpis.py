"""
KPIs Page

Displays detailed Key Performance Indicators with interactive cards.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def show_kpis(kpis):
    """
    Display KPIs page.
    
    Args:
        kpis: KPI dictionary
    """
    st.header("Key Performance Indicators")
    
    if kpis is None:
        st.warning("No KPI data available. Please process data first.")
        return
    
    # Data period information
    data_period = kpis.get("data_period", {})
    st.subheader("Data Period")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Start Date", data_period.get("start", "N/A"))
    
    with col2:
        st.metric("End Date", data_period.get("end", "N/A"))
    
    with col3:
        st.metric("Total Days", data_period.get("total_days", 0))
    
    st.markdown("---")
    
    # Current Status KPIs
    st.subheader("Current Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Total Children Under Care",
            f"{kpis.get('total_children_under_care', 0):,.0f}",
            delta="Latest Value"
        )
    
    with col2:
        st.metric(
            "Average System Load",
            f"{kpis.get('average_system_load', 0):,.0f}",
            delta="Overall Average"
        )
    
    st.markdown("---")
    
    # Daily Averages
    st.subheader("Daily Averages")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Average Daily Intake",
            f"{kpis.get('average_daily_intake', 0):,.0f}",
            delta="Transfers"
        )
    
    with col2:
        st.metric(
            "Average Daily Discharges",
            f"{kpis.get('average_daily_discharges', 0):,.0f}",
            delta="Discharges"
        )
    
    with col3:
        st.metric(
            "Average CBP Load",
            f"{kpis.get('average_cbp_load', 0):,.0f}",
            delta="CBP Custody"
        )
    
    with col4:
        st.metric(
            "Average HHS Load",
            f"{kpis.get('average_hhs_load', 0):,.0f}",
            delta="HHS Care"
        )
    
    st.markdown("---")
    
    # Pressure Indicators
    st.subheader("Pressure Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        net_pressure = kpis.get('net_intake_pressure', 0)
        delta_color = "normal" if net_pressure > 0 else "inverse"
        st.metric(
            "Net Intake Pressure",
            f"{net_pressure:,.0f}",
            delta=f"{net_pressure:+,.0f}",
            delta_color=delta_color
        )
    
    with col2:
        volatility = kpis.get('care_load_volatility_index', 0)
        st.metric(
            "Volatility Index",
            f"{volatility:.3f}",
            delta="Stability"
        )
    
    with col3:
        backlog_rate = kpis.get('backlog_accumulation_rate', 0)
        st.metric(
            "Backlog Accumulation Rate",
            f"{backlog_rate:,.0f}/day",
            delta="Daily Change"
        )
    
    with col4:
        discharge_ratio = kpis.get('discharge_offset_ratio', 0)
        st.metric(
            "Discharge Offset Ratio",
            f"{discharge_ratio:.3f}",
            delta="Ratio"
        )
    
    # Pressure indicator interpretation
    st.info("**Pressure Indicator Interpretation:**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Net Intake Pressure:**")
        if net_pressure > 100:
            st.markdown("🔴 High pressure - Intake significantly exceeds discharges")
        elif net_pressure > 50:
            st.markdown("🟡 Moderate pressure - Intake exceeds discharges")
        elif net_pressure > 0:
            st.markdown("🟢 Low pressure - Slight intake excess")
        else:
            st.markdown("🟢 Negative - Discharges exceed intake")
    
    with col2:
        st.markdown("**Volatility Index:**")
        if volatility > 0.5:
            st.markdown("🔴 High volatility - Unstable operations")
        elif volatility > 0.3:
            st.markdown("🟡 Moderate volatility - Some fluctuation")
        else:
            st.markdown("🟢 Low volatility - Stable operations")
    
    st.markdown("---")
    
    # Extreme Values
    st.subheader("Extreme Values")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Peak Load Day")
        peak = kpis.get("peak_load_day", {})
        st.markdown(f"**Date:** {peak.get('date', 'N/A')}")
        st.markdown(f"**Value:** {peak.get('value', 0):,.0f}")
        
        st.markdown("### Highest Intake")
        highest_intake = kpis.get("highest_intake", {})
        st.markdown(f"**Date:** {highest_intake.get('date', 'N/A')}")
        st.markdown(f"**Value:** {highest_intake.get('value', 0):,.0f}")
    
    with col2:
        st.markdown("### Lowest Load Day")
        lowest = kpis.get("lowest_load_day", {})
        st.markdown(f"**Date:** {lowest.get('date', 'N/A')}")
        st.markdown(f"**Value:** {lowest.get('value', 0):,.0f}")
        
        st.markdown("### Highest Discharge")
        highest_discharge = kpis.get("highest_discharge", {})
        st.markdown(f"**Date:** {highest_discharge.get('date', 'N/A')}")
        st.markdown(f"**Value:** {highest_discharge.get('value', 0):,.0f}")
    
    st.markdown("---")
    
    # KPI Comparison Chart
    st.subheader("KPI Comparison")
    
    # Create comparison chart for key KPIs
    kpi_names = [
        "Average Daily Intake",
        "Average Daily Discharges",
        "Average CBP Load",
        "Average HHS Load"
    ]
    
    kpi_values = [
        kpis.get("average_daily_intake", 0),
        kpis.get("average_daily_discharges", 0),
        kpis.get("average_cbp_load", 0),
        kpis.get("average_hhs_load", 0)
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=kpi_names,
        y=kpi_values,
        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd']
    ))
    
    fig.update_layout(
        title="Key KPI Comparison",
        xaxis_title="KPI",
        yaxis_title="Value",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Detailed KPI Table
    st.subheader("Detailed KPI Table")
    
    # Create detailed table
    kpi_table_data = []
    for key, value in kpis.items():
        if key in ["calculation_timestamp", "data_period"]:
            continue
        if isinstance(value, dict):
            continue
        
        kpi_table_data.append({
            "KPI": key.replace("_", " ").title(),
            "Value": value
        })
    
    kpi_df = pd.DataFrame(kpi_table_data)
    st.dataframe(kpi_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Export KPIs
    st.subheader("Export KPIs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export KPIs as JSON"):
            import json
            kpi_json = json.dumps(kpis, indent=2, default=str)
            st.download_button(
                label="Download JSON",
                data=kpi_json,
                file_name="kpis.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("Export KPIs as CSV"):
            kpi_csv = kpi_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=kpi_csv,
                file_name="kpis.csv",
                mime="text/csv"
            )

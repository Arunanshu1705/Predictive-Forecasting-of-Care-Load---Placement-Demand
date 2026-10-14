"""
Backlog/Pressure Analysis Page

Displays backlog analysis, pressure windows, and net intake pressure.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def show_pressure_analysis(df, analytics):
    """
    Display pressure analysis page.
    
    Args:
        df: DataFrame with processed data
        analytics: Analytics results dictionary
    """
    st.header("Pressure Analysis")
    
    if df is None:
        st.warning("No data available. Please process data first.")
        return
    
    date_col = "Date"
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col])
    
    # Backlog Analysis
    st.subheader("Backlog Analysis")
    
    backlog_analysis = analytics.get("backlog_analysis", {})
    
    if backlog_analysis.get("status") != "SKIPPED":
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Current Backlog",
                f"{backlog_analysis.get('current_backlog', 0):,.0f}"
            )
        
        with col2:
            st.metric(
                "Trend",
                backlog_analysis.get("trend_status", "N/A")
            )
        
        with col3:
            st.metric(
                "Max Backlog",
                f"{backlog_analysis.get('max_backlog', 0):,.0f}"
            )
        
        with col4:
            st.metric(
                "Accumulation Rate",
                f"{backlog_analysis.get('accumulation_rate', 0):.0f}/day"
            )
        
        # Plot backlog indicator
        if "Backlog_Indicator" in df.columns:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df[date_col],
                y=df["Backlog_Indicator"],
                mode='lines',
                name='Backlog Indicator',
                line=dict(color='#d62728'),
                fill='tozeroy'
            ))
            
            fig.update_layout(
                title="Backlog Indicator Over Time",
                xaxis_title="Date",
                yaxis_title="Backlog",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Pressure Windows
    st.subheader("Pressure Windows Analysis")
    
    pressure_windows = analytics.get("pressure_windows", {})
    
    if pressure_windows.get("status") != "SKIPPED":
        windows_data = pressure_windows.get("windows", {})
        
        # Display pressure metrics for each window
        for window_name, window_data in windows_data.items():
            st.write(f"**{window_name.replace('_', ' ').title()}**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Average Pressure",
                    f"{window_data.get('average_pressure', 0):.0f}"
                )
            
            with col2:
                st.metric(
                    "Max Pressure",
                    f"{window_data.get('max_pressure', 0):.0f}"
                )
            
            with col3:
                st.metric(
                    "High Pressure Days",
                    f"{window_data.get('high_pressure_days', 0)} ({window_data.get('high_pressure_percentage', 0):.1f}%)"
                )
            
            st.markdown("---")
        
        # Overall pressure status
        overall_status = pressure_windows.get("overall_pressure_status", "N/A")
        
        status_colors = {
            "LOW": "🟢",
            "MODERATE": "🟡",
            "HIGH": "🟠",
            "CRITICAL": "🔴"
        }
        
        status_emoji = status_colors.get(overall_status, "⚪")
        st.info(f"**Overall Pressure Status:** {status_emoji} {overall_status}")
    
    st.markdown("---")
    
    # Net Intake Pressure
    st.subheader("Net Intake Pressure")
    
    if "Net_Daily_Intake" in df.columns:
        fig = go.Figure()
        
        # Plot net intake
        fig.add_trace(go.Scatter(
            x=df[date_col],
            y=df["Net_Daily_Intake"],
            mode='lines',
            name='Net Daily Intake',
            line=dict(color='#1f77b4')
        ))
        
        # Add rolling means
        if "Net_Daily_Intake_Rolling_Mean_7d" in df.columns:
            fig.add_trace(go.Scatter(
                x=df[date_col],
                y=df["Net_Daily_Intake_Rolling_Mean_7d"],
                mode='lines',
                name='7-Day Rolling Mean',
                line=dict(color='#ff7f0e')
            ))
        
        if "Net_Daily_Intake_Rolling_Mean_14d" in df.columns:
            fig.add_trace(go.Scatter(
                x=df[date_col],
                y=df["Net_Daily_Intake_Rolling_Mean_14d"],
                mode='lines',
                name='14-Day Rolling Mean',
                line=dict(color='#2ca02c')
            ))
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        fig.update_layout(
            title="Net Intake Pressure Over Time",
            xaxis_title="Date",
            yaxis_title="Net Intake",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Net intake statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Max Net Intake", f"{df['Net_Daily_Intake'].max():,.0f}")
        
        with col2:
            st.metric("Min Net Intake", f"{df['Net_Daily_Intake'].min():,.0f}")
        
        with col3:
            st.metric("Average Net Intake", f"{df['Net_Daily_Intake'].mean():,.0f}")
    
    st.markdown("---")
    
    # Discharge Offset Analysis
    st.subheader("Discharge Offset Analysis")
    
    if "Discharge_Offset_Ratio" in df.columns:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df[date_col],
            y=df["Discharge_Offset_Ratio"],
            mode='lines',
            name='Discharge Offset Ratio',
            line=dict(color='#9467bd')
        ))
        
        # Add reference line at 1.0 (perfect offset)
        fig.add_hline(y=1.0, line_dash="dash", line_color="green", annotation_text="Perfect Offset")
        
        fig.update_layout(
            title="Discharge Offset Ratio Over Time",
            xaxis_title="Date",
            yaxis_title="Ratio (Discharges/Transfers)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Discharge offset statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Average Ratio", f"{df['Discharge_Offset_Ratio'].mean():.3f}")
        
        with col2:
            st.metric("Max Ratio", f"{df['Discharge_Offset_Ratio'].max():.3f}")
        
        with col3:
            st.metric("Min Ratio", f"{df['Discharge_Offset_Ratio'].min():.3f}")
        
        # Interpretation
        avg_ratio = df['Discharge_Offset_Ratio'].mean()
        if avg_ratio >= 0.9:
            interpretation = "Excellent - Discharges nearly match transfers"
        elif avg_ratio >= 0.7:
            interpretation = "Good - Discharges keeping pace with transfers"
        elif avg_ratio >= 0.5:
            interpretation = "Moderate - Some backlog accumulation"
        else:
            interpretation = "Poor - Significant backlog accumulation"
        
        st.info(f"**Interpretation:** {interpretation}")
    
    st.markdown("---")
    
    # Pressure Heatmap (by day of week and month)
    st.subheader("Pressure Patterns")
    
    if "Net_Daily_Intake" in df.columns and "Day_of_Week" in df.columns:
        # Create pivot table for heatmap
        df_temp = df.copy()
        df_temp["Day_Name"] = df_temp[date_col].dt.day_name()
        df_temp["Month_Name"] = df_temp[date_col].dt.month_name()
        
        # Aggregate by day of week
        day_pressure = df_temp.groupby("Day_Name")["Net_Daily_Intake"].mean().reindex(
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        )
        
        # Bar chart of pressure by day
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=day_pressure.index,
            y=day_pressure.values,
            marker_color='#1f77b4'
        ))
        
        fig.update_layout(
            title="Average Net Intake by Day of Week",
            xaxis_title="Day",
            yaxis_title="Average Net Intake",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

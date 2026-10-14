"""
Trends Page

Displays trend analysis including daily, weekly, and monthly trends.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


def show_trends(df, analytics):
    """
    Display trends page.
    
    Args:
        df: DataFrame with processed data
        analytics: Analytics results dictionary
    """
    st.header("Trend Analysis")
    
    if df is None:
        st.warning("No data available. Please process data first.")
        return
    
    date_col = "Date"
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col])
    
    # Granularity selector
    st.subheader("Trend Visualization")
    
    granularity = st.selectbox(
        "Select Granularity",
        ["Daily", "Weekly", "Monthly"],
        index=0
    )
    
    # Aggregate data based on granularity
    df_agg = df.copy()
    
    if granularity == "Weekly":
        df_agg["Week"] = df_agg[date_col].dt.isocalendar().week
        df_agg["Year"] = df_agg[date_col].dt.year
        df_agg = df_agg.groupby(["Year", "Week"]).agg({
            "Transfers": "sum",
            "Discharges": "sum",
            "HHS Care": "mean",
            "CBP Custody": "mean",
            "Total_System_Load": "mean"
        }).reset_index()
        df_agg["Period"] = df_agg["Year"].astype(str) + "-W" + df_agg["Week"].astype(str)
        x_col = "Period"
    elif granularity == "Monthly":
        df_agg["YearMonth"] = df_agg[date_col].dt.to_period('M')
        df_agg = df_agg.groupby("YearMonth").agg({
            "Transfers": "sum",
            "Discharges": "sum",
            "HHS Care": "mean",
            "CBP Custody": "mean",
            "Total_System_Load": "mean"
        }).reset_index()
        df_agg["Period"] = df_agg["YearMonth"].astype(str)
        x_col = "Period"
    else:
        x_col = date_col
    
    # Daily Intake Trends
    st.subheader("Intake Trends")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if "Transfers" in df_agg.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_agg[x_col],
                y=df_agg["Transfers"],
                mode='lines+markers',
                name='Transfers',
                line=dict(color='#1f77b4')
            ))
            fig.update_layout(
                title=f"Transfers ({granularity})",
                xaxis_title="Period",
                yaxis_title="Count",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if "Discharges" in df_agg.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_agg[x_col],
                y=df_agg["Discharges"],
                mode='lines+markers',
                name='Discharges',
                line=dict(color='#ff7f0e')
            ))
            fig.update_layout(
                title=f"Discharges ({granularity})",
                xaxis_title="Period",
                yaxis_title="Count",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Load Trends
    st.subheader("Load Trends")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if "HHS Care" in df_agg.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_agg[x_col],
                y=df_agg["HHS Care"],
                mode='lines+markers',
                name='HHS Care',
                line=dict(color='#2ca02c')
            ))
            fig.update_layout(
                title=f"HHS Care ({granularity})",
                xaxis_title="Period",
                yaxis_title="Count",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if "CBP Custody" in df_agg.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_agg[x_col],
                y=df_agg["CBP Custody"],
                mode='lines+markers',
                name='CBP Custody',
                line=dict(color='#9467bd')
            ))
            fig.update_layout(
                title=f"CBP Custody ({granularity})",
                xaxis_title="Period",
                yaxis_title="Count",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Net Intake Trend
    st.subheader("Net Intake Trend")
    
    net_intake_trend = analytics.get("net_intake_trend", {})
    
    if net_intake_trend.get("status") != "SKIPPED":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Trend Direction",
                net_intake_trend.get("trend_direction", "N/A")
            )
        
        with col2:
            st.metric(
                "Current Value",
                f"{net_intake_trend.get('current_value', 0):,.0f}"
            )
        
        with col3:
            st.metric(
                "Status",
                net_intake_trend.get("status", "N/A")
            )
        
        # Plot net intake
        if "Net_Daily_Intake" in df.columns:
            fig = go.Figure()
            
            if granularity == "Daily":
                fig.add_trace(go.Scatter(
                    x=df[date_col],
                    y=df["Net_Daily_Intake"],
                    mode='lines',
                    name='Net Daily Intake',
                    line=dict(color='#d62728')
                ))
                
                # Add zero line
                fig.add_hline(y=0, line_dash="dash", line_color="gray")
                
                fig.update_layout(
                    title="Net Daily Intake Over Time",
                    xaxis_title="Date",
                    yaxis_title="Net Intake",
                    hovermode='x unified',
                    height=400
                )
            else:
                # Aggregate net intake
                df_net = df.copy()
                if granularity == "Weekly":
                    df_net["Week"] = df_net[date_col].dt.isocalendar().week
                    df_net["Year"] = df_net[date_col].dt.year
                    df_net = df_net.groupby(["Year", "Week"])["Net_Daily_Intake"].sum().reset_index()
                    df_net["Period"] = df_net["Year"].astype(str) + "-W" + df_net["Week"].astype(str)
                elif granularity == "Monthly":
                    df_net["YearMonth"] = df_net[date_col].dt.to_period('M')
                    df_net = df_net.groupby("YearMonth")["Net_Daily_Intake"].sum().reset_index()
                    df_net["Period"] = df_net["YearMonth"].astype(str)
                
                fig.add_trace(go.Scatter(
                    x=df_net["Period"],
                    y=df_net["Net_Daily_Intake"],
                    mode='lines+markers',
                    name='Net Intake',
                    line=dict(color='#d62728')
                ))
                
                fig.add_hline(y=0, line_dash="dash", line_color="gray")
                
                fig.update_layout(
                    title=f"Net Intake ({granularity})",
                    xaxis_title="Period",
                    yaxis_title="Net Intake",
                    height=400
                )
            
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Growth Trend
    st.subheader("Growth Trend Analysis")
    
    growth_trend = analytics.get("growth_trend", {})
    
    if growth_trend.get("status") != "SKIPPED":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Growth Status",
                growth_trend.get("growth_status", "N/A")
            )
        
        with col2:
            st.metric(
                "Total Growth",
                f"{growth_trend.get('total_growth_percent', 0):.1f}%"
            )
        
        with col3:
            st.metric(
                "Avg Daily Growth",
                f"{growth_trend.get('average_daily_growth_percent', 0):.2f}%"
            )
        
        # Plot growth rate
        if "Daily_Growth_Rate" in df.columns:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df[date_col],
                y=df["Daily_Growth_Rate"],
                mode='lines',
                name='Daily Growth Rate',
                line=dict(color='#17becf')
            ))
            
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            
            fig.update_layout(
                title="Daily Growth Rate Over Time",
                xaxis_title="Date",
                yaxis_title="Growth Rate (%)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Variance Analysis
    st.subheader("Variance Patterns")
    
    variance_patterns = analytics.get("variance_patterns", {})
    
    if variance_patterns.get("status") != "SKIPPED":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Volatility Status",
                variance_patterns.get("volatility_status", "N/A")
            )
        
        with col2:
            st.metric(
                "Overall Variance",
                f"{variance_patterns.get('overall_variance', 0):.0f}"
            )
        
        with col3:
            st.metric(
                "High Volatility Days",
                variance_patterns.get("high_volatility_days", 0)
            )

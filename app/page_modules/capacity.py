"""
Capacity Page

Displays capacity analysis including CBP vs HHS comparison and system load.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def show_capacity(df, analytics):
    """
    Display capacity page.
    
    Args:
        df: DataFrame with processed data
        analytics: Analytics results dictionary
    """
    st.header("Capacity Analysis")
    
    if df is None:
        st.warning("No data available. Please process data first.")
        return
    
    date_col = "Date"
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col])
    
    # Capacity Stress Analysis
    st.subheader("Capacity Stress Detection")
    
    capacity_stress = analytics.get("capacity_stress", {})
    
    if capacity_stress.get("status") != "SKIPPED":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Stress Status",
                capacity_stress.get("status", "N/A")
            )
        
        with col2:
            st.metric(
                "Stress Days",
                capacity_stress.get("stress_days", 0)
            )
        
        with col3:
            st.metric(
                "Stress Percentage",
                f"{capacity_stress.get('stress_percentage', 0):.1f}%"
            )
        
        # Stress periods
        stress_periods = capacity_stress.get("stress_periods", [])
        if stress_periods:
            st.write("**Stress Periods:**")
            for period in stress_periods:
                st.write(f"- {period['start']} to {period['end']} ({period['duration_days']} days)")
    
    st.markdown("---")
    
    # CBP vs HHS Comparison
    st.subheader("CBP Custody vs HHS Care")
    
    if "CBP Custody" in df.columns and "HHS Care" in df.columns:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df[date_col],
            y=df["CBP Custody"],
            mode='lines',
            name='CBP Custody',
            line=dict(color='#1f77b4')
        ))
        
        fig.add_trace(go.Scatter(
            x=df[date_col],
            y=df["HHS Care"],
            mode='lines',
            name='HHS Care',
            line=dict(color='#2ca02c')
        ))
        
        fig.update_layout(
            title="CBP Custody vs HHS Care Over Time",
            xaxis_title="Date",
            yaxis_title="Count",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Total System Load
    st.subheader("Total System Load")
    
    if "Total_System_Load" in df.columns:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df[date_col],
            y=df["Total_System_Load"],
            mode='lines',
            name='Total System Load',
            line=dict(color='#ff7f0e'),
            fill='tozeroy'
        ))
        
        fig.update_layout(
            title="Total System Load Over Time",
            xaxis_title="Date",
            yaxis_title="Count",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # System load statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Max Load", f"{df['Total_System_Load'].max():,.0f}")
        
        with col2:
            st.metric("Min Load", f"{df['Total_System_Load'].min():,.0f}")
        
        with col3:
            st.metric("Average Load", f"{df['Total_System_Load'].mean():,.0f}")
    
    st.markdown("---")
    
    # High Load Periods
    st.subheader("High Load Periods")
    
    high_load_periods = analytics.get("high_load_periods", {})
    
    if high_load_periods.get("status") != "SKIPPED":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "High Load Days",
                high_load_periods.get("high_load_days", 0)
            )
        
        with col2:
            st.metric(
                "Critical Load Days",
                high_load_periods.get("critical_load_days", 0)
            )
        
        with col3:
            st.metric(
                "Max High Load Duration",
                f"{high_load_periods.get('max_high_load_duration', 0)} days"
            )
        
        # High load periods details
        high_periods = high_load_periods.get("high_load_periods", [])
        if high_periods:
            st.write("**High Load Periods:**")
            for period in high_periods:
                st.write(f"- {period['start']} to {period['end']} ({period['duration']} days)")
        
        critical_periods = high_load_periods.get("critical_load_periods", [])
        if critical_periods:
            st.write("**Critical Load Periods:**")
            for period in critical_periods:
                st.write(f"- {period['start']} to {period['end']} ({period['duration']} days)")
    
    st.markdown("---")
    
    # Moving Average Signals
    st.subheader("Moving Average Analysis")
    
    ma_signals = analytics.get("moving_average_signals", {})
    
    if ma_signals.get("status") != "SKIPPED":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Current Signal",
                ma_signals.get("current_signal", "N/A")
            )
        
        with col2:
            st.metric(
                "Signal Strength",
                ma_signals.get("signal_strength", "N/A")
            )
        
        with col3:
            st.metric(
                "Crossover Count",
                ma_signals.get("crossover_count", 0)
            )
        
        # Display moving averages if available
        load_col = "HHS Care" if "HHS Care" in df.columns else "Total_System_Load"
        ma_7_col = f"{load_col}_Rolling_Mean_7d"
        ma_14_col = f"{load_col}_Rolling_Mean_14d"
        
        if ma_7_col in df.columns and ma_14_col in df.columns:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df[date_col],
                y=df[ma_7_col],
                mode='lines',
                name='7-Day MA',
                line=dict(color='#1f77b4')
            ))
            
            fig.add_trace(go.Scatter(
                x=df[date_col],
                y=df[ma_14_col],
                mode='lines',
                name='14-Day MA',
                line=dict(color='#ff7f0e')
            ))
            
            if load_col in df.columns:
                fig.add_trace(go.Scatter(
                    x=df[date_col],
                    y=df[load_col],
                    mode='lines',
                    name='Daily Values',
                    line=dict(color='#2ca02c', dash='dot'),
                    opacity=0.5
                ))
            
            fig.update_layout(
                title=f"Moving Averages: {load_col}",
                xaxis_title="Date",
                yaxis_title="Count",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)

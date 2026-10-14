"""
Insights Page

Displays automatically generated insights based on analytics results.
"""

import streamlit as st
import pandas as pd


def show_insights(analytics, validation):
    """
    Display insights page.
    
    Args:
        analytics: Analytics results dictionary
        validation: Validation results dictionary
    """
    st.header("Automated Insights")
    
    if analytics is None:
        st.warning("No analytics data available. Please process data first.")
        return
    
    # Overall Assessment
    st.subheader("Overall System Assessment")
    
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
    st.markdown(f"### {status_emoji} System Status: {overall_status}")
    
    recommendation = overall_assessment.get("recommendation", "")
    if recommendation:
        st.success(f"**Recommendation:** {recommendation}")
    
    warnings = overall_assessment.get("warnings", [])
    if warnings:
        st.warning("**Active Warnings:**")
        for warning in warnings:
            st.markdown(f"• {warning}")
    
    st.markdown("---")
    
    # Capacity Insights
    st.subheader("Capacity Insights")
    
    capacity_stress = analytics.get("capacity_stress", {})
    
    if capacity_stress.get("status") != "SKIPPED":
        stress_status = capacity_stress.get("status", "N/A")
        stress_days = capacity_stress.get("stress_days", 0)
        stress_percentage = capacity_stress.get("stress_percentage", 0)
        
        st.info(f"**Capacity Stress Status:** {stress_status}")
        
        if stress_status == "HIGH_STRESS":
            st.error("⚠️ **Critical Insight:** System is experiencing high capacity stress. Immediate action required to expand capacity or increase discharge processing.")
        elif stress_status == "MODERATE_STRESS":
            st.warning("⚠️ **Insight:** System is under moderate capacity stress. Monitor closely and prepare contingency plans.")
        else:
            st.success("✅ **Insight:** System capacity is within normal parameters.")
        
        st.write(f"- Stress Days: {stress_days} ({stress_percentage:.1f}% of period)")
        st.write(f"- Max Stress Duration: {capacity_stress.get('max_stress_duration', 0)} days")
    
    # High Load Periods
    high_load_periods = analytics.get("high_load_periods", {})
    if high_load_periods.get("status") != "SKIPPED":
        critical_days = high_load_periods.get("critical_load_days", 0)
        
        if critical_days > 0:
            st.error(f"⚠️ **Critical Insight:** {critical_days} days with critical load levels detected.")
        else:
            st.success("✅ **Insight:** No critical load periods detected.")
    
    st.markdown("---")
    
    # Backlog Insights
    st.subheader("Backlog Insights")
    
    backlog_analysis = analytics.get("backlog_analysis", {})
    
    if backlog_analysis.get("status") != "SKIPPED":
        backlog_trend = backlog_analysis.get("trend_status", "N/A")
        current_backlog = backlog_analysis.get("current_backlog", 0)
        accumulation_rate = backlog_analysis.get("accumulation_rate", 0)
        
        st.info(f"**Backlog Trend:** {backlog_trend}")
        
        if backlog_trend == "INCREASING":
            st.error("⚠️ **Critical Insight:** Backlog is increasing over time. This indicates that intake is consistently exceeding discharge capacity.")
            st.write(f"- Current Backlog: {current_backlog:,.0f}")
            st.write(f"- Accumulation Rate: {accumulation_rate:.0f} per day")
            st.write("**Recommendation:** Increase discharge processing capacity and review placement procedures.")
        elif backlog_trend == "DECREASING":
            st.success("✅ **Insight:** Backlog is decreasing over time. Discharge processing is keeping pace with or exceeding intake.")
        else:
            st.info("ℹ️ **Insight:** Backlog is stable. Intake and discharge are balanced.")
    
    st.markdown("---")
    
    # Pressure Insights
    st.subheader("Pressure Insights")
    
    pressure_windows = analytics.get("pressure_windows", {})
    
    if pressure_windows.get("status") != "SKIPPED":
        overall_pressure = pressure_windows.get("overall_pressure_status", "N/A")
        
        st.info(f"**Overall Pressure Status:** {overall_pressure}")
        
        if overall_pressure == "CRITICAL":
            st.error("⚠️ **Critical Insight:** System is under critical pressure across multiple time windows. Emergency response required.")
        elif overall_pressure == "HIGH":
            st.warning("⚠️ **Insight:** System is experiencing high pressure. Activate contingency protocols.")
        elif overall_pressure == "MODERATE":
            st.info("ℹ️ **Insight:** System is under moderate pressure. Continue monitoring.")
        else:
            st.success("✅ **Insight:** System pressure is within normal limits.")
        
        # Window-specific insights
        windows_data = pressure_windows.get("windows", {})
        for window_name, window_data in windows_data.items():
            high_pressure_pct = window_data.get("high_pressure_percentage", 0)
            
            if high_pressure_pct > 30:
                st.warning(f"⚠️ {window_name}: {high_pressure_pct:.1f}% high-pressure days detected")
            elif high_pressure_pct > 20:
                st.info(f"ℹ️ {window_name}: {high_pressure_pct:.1f}% high-pressure days detected")
    
    st.markdown("---")
    
    # Growth Insights
    st.subheader("Growth Insights")
    
    growth_trend = analytics.get("growth_trend", {})
    
    if growth_trend.get("status") != "SKIPPED":
        growth_status = growth_trend.get("growth_status", "N/A")
        total_growth = growth_trend.get("total_growth_percent", 0)
        avg_daily_growth = growth_trend.get("average_daily_growth_percent", 0)
        
        st.info(f"**Growth Status:** {growth_status}")
        
        if growth_status == "RAPID_GROWTH":
            st.warning("⚠️ **Insight:** System is experiencing rapid growth. Ensure adequate staffing and resource planning.")
            st.write(f"- Total Growth: {total_growth:.1f}%")
            st.write(f"- Average Daily Growth: {avg_daily_growth:.2f}%")
        elif growth_status == "MODERATE_GROWTH":
            st.info("ℹ️ **Insight:** System is experiencing moderate growth. Standard capacity planning should suffice.")
        elif growth_status == "SLOW_GROWTH":
            st.success("✅ **Insight:** System is experiencing slow growth. Current capacity planning is adequate.")
        else:
            st.info("ℹ️ **Insight:** System is experiencing decline or stability.")
    
    st.markdown("---")
    
    # Net Intake Insights
    st.subheader("Net Intake Insights")
    
    net_intake_trend = analytics.get("net_intake_trend", {})
    
    if net_intake_trend.get("status") != "SKIPPED":
        trend_direction = net_intake_trend.get("trend_direction", "N/A")
        net_status = net_intake_trend.get("status", "N/A")
        current_value = net_intake_trend.get("current_value", 0)
        historical_avg = net_intake_trend.get("historical_average", 0)
        
        st.info(f"**Trend Direction:** {trend_direction}")
        
        if net_status == "HIGH_PRESSURE":
            st.error("⚠️ **Critical Insight:** Current net intake is significantly above historical average. System under pressure.")
            st.write(f"- Current: {current_value:,.0f}")
            st.write(f"- Historical Average: {historical_avg:,.0f}")
            st.write(f"- Deviation: {current_value - historical_avg:+,.0f}")
        elif net_status == "LOW_PRESSURE":
            st.success("✅ **Insight:** Current net intake is below historical average. System operating efficiently.")
        else:
            st.info("ℹ️ **Insight:** Net intake is within normal range.")
    
    st.markdown("---")
    
    # Moving Average Insights
    st.subheader("Moving Average Signals")
    
    ma_signals = analytics.get("moving_average_signals", {})
    
    if ma_signals.get("status") != "SKIPPED":
        current_signal = ma_signals.get("current_signal", "N/A")
        signal_strength = ma_signals.get("signal_strength", "N/A")
        
        st.info(f"**Current Signal:** {current_signal}")
        st.info(f"**Signal Strength:** {signal_strength}")
        
        if current_signal == "BULLISH" and signal_strength == "STRONG":
            st.success("✅ **Insight:** Strong bullish signal - Short-term trend is above long-term trend, indicating positive momentum.")
        elif current_signal == "BEARISH" and signal_strength == "STRONG":
            st.warning("⚠️ **Insight:** Strong bearish signal - Short-term trend is below long-term trend, indicating negative momentum.")
        else:
            st.info("ℹ️ **Insight:** Moving averages show mixed or weak signals.")
    
    st.markdown("---")
    
    # Variance Insights
    st.subheader("Variance Insights")
    
    variance_patterns = analytics.get("variance_patterns", {})
    
    if variance_patterns.get("status") != "SKIPPED":
        volatility_status = variance_patterns.get("volatility_status", "N/A")
        high_volatility_days = variance_patterns.get("high_volatility_days", 0)
        
        st.info(f"**Volatility Status:** {volatility_status}")
        
        if volatility_status == "HIGH":
            st.warning("⚠️ **Insight:** High volatility detected. System operations are unstable. Review operational procedures.")
            st.write(f"- High Volatility Days: {high_volatility_days}")
        elif volatility_status == "MODERATE":
            st.info("ℹ️ **Insight:** Moderate volatility. Some operational fluctuation is normal.")
        else:
            st.success("✅ **Insight:** Low volatility. System operations are stable.")
    
    st.markdown("---")
    
    # Data Quality Insights
    st.subheader("Data Quality Insights")
    
    if validation is not None:
        overall_status = validation.get("overall_status", "N/A")
        
        st.info(f"**Validation Status:** {overall_status}")
        
        if overall_status == "PASS":
            st.success("✅ **Insight:** All data validation checks passed. Data quality is excellent.")
        elif overall_status == "WARNING":
            st.warning("⚠️ **Insight:** Some validation checks raised warnings. Review data quality.")
        else:
            st.error("❌ **Insight:** Data validation failed. Critical data quality issues detected.")
        
        failed_checks = validation.get("failed_checks", [])
        warning_checks = validation.get("warning_checks", [])
        
        if failed_checks:
            st.error("**Failed Checks:**")
            for check in failed_checks:
                st.markdown(f"• {check}")
        
        if warning_checks:
            st.warning("**Warning Checks:**")
            for check in warning_checks:
                st.markdown(f"• {check}")
    
    st.markdown("---")
    
    # Summary of Key Findings
    st.subheader("Summary of Key Findings")
    
    findings = []
    
    # Capacity findings
    if capacity_stress.get("status") == "HIGH_STRESS":
        findings.append("🔴 System under high capacity stress")
    elif capacity_stress.get("status") == "MODERATE_STRESS":
        findings.append("🟡 System under moderate capacity stress")
    
    # Backlog findings
    if backlog_analysis.get("trend_status") == "INCREASING":
        findings.append("🔴 Backlog is increasing")
    elif backlog_analysis.get("trend_status") == "DECREASING":
        findings.append("🟢 Backlog is decreasing")
    
    # Pressure findings
    if pressure_windows.get("overall_pressure_status") == "CRITICAL":
        findings.append("🔴 Critical pressure levels detected")
    elif pressure_windows.get("overall_pressure_status") == "HIGH":
        findings.append("🟠 High pressure levels detected")
    
    # Growth findings
    if growth_trend.get("growth_status") == "RAPID_GROWTH":
        findings.append("🟠 Rapid growth detected")
    
    # Net intake findings
    if net_intake_trend.get("status") == "HIGH_PRESSURE":
        findings.append("🔴 High net intake pressure")
    
    # Variance findings
    if variance_patterns.get("volatility_status") == "HIGH":
        findings.append("🟠 High volatility detected")
    
    if findings:
        st.write("**Key Findings:**")
        for finding in findings:
            st.markdown(f"- {finding}")
    else:
        st.success("✅ No critical issues detected. System is operating normally.")
    
    st.markdown("---")
    
    # Action Items
    st.subheader("Recommended Action Items")
    
    action_items = []
    
    if capacity_stress.get("status") in ["HIGH_STRESS", "MODERATE_STRESS"]:
        action_items.append("Review capacity expansion options")
        action_items.append("Activate overflow facilities if available")
    
    if backlog_analysis.get("trend_status") == "INCREASING":
        action_items.append("Increase discharge processing capacity")
        action_items.append("Review placement procedures")
        action_items.append("Allocate additional staff for discharge processing")
    
    if pressure_windows.get("overall_pressure_status") in ["CRITICAL", "HIGH"]:
        action_items.append("Activate contingency protocols")
        action_items.append("Implement emergency response procedures")
    
    if growth_trend.get("growth_status") == "RAPID_GROWTH":
        action_items.append("Update intake forecasting models")
        action_items.append("Review staffing requirements")
        action_items.append("Plan for additional capacity")
    
    if variance_patterns.get("volatility_status") == "HIGH":
        action_items.append("Review operational procedures for stability")
        action_items.append("Investigate causes of operational fluctuation")
    
    if action_items:
        st.write("**Priority Actions:**")
        for i, item in enumerate(action_items, 1):
            st.markdown(f"{i}. {item}")
    else:
        st.info("No immediate action items required. Continue standard monitoring.")

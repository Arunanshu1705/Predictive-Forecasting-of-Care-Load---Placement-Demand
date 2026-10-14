"""
Visualization Module

This module generates professional charts and visualizations for analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.logger import get_logger
from backend.utils import load_config, ensure_directory


class Visualizer:
    """
    Visualization class for HHS UAC Program data.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Visualizer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or load_config()
        self.logger = get_logger(__name__)
        self.df: Optional[pd.DataFrame] = None
        self.figures: Dict[str, Any] = {}
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (
            self.config["visualization"]["figure_size"]["width"],
            self.config["visualization"]["figure_size"]["height"]
        )
        
    def load_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load featured data for visualization.
        
        Args:
            file_path: Path to featured data file
            
        Returns:
            Loaded DataFrame
        """
        if file_path is None:
            file_path = "data/processed/featured_data.csv"
        
        self.logger.info(f"Loading data for visualization: {file_path}")
        
        try:
            self.df = pd.read_csv(file_path, encoding='utf-8')
            # Convert date column
            date_col = self.config["data"]["date_column"]
            self.df[date_col] = pd.to_datetime(self.df[date_col])
            self.logger.info(f"Loaded {len(self.df)} rows for visualization")
            return self.df
        except UnicodeDecodeError:
            self.df = pd.read_csv(file_path, encoding='latin1')
            date_col = self.config["data"]["date_column"]
            self.df[date_col] = pd.to_datetime(self.df[date_col])
            self.logger.info(f"Loaded {len(self.df)} rows for visualization with latin1 encoding")
            return self.df
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise
    
    def plot_daily_intake(self, save: bool = True) -> go.Figure:
        """
        Create daily intake line chart.
        
        Args:
            save: Whether to save the figure
            
        Returns:
            Plotly figure
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Creating daily intake chart")
        
        date_col = self.config["data"]["date_column"]
        
        fig = go.Figure()
        
        if "Transfers" in self.df.columns:
            fig.add_trace(go.Scatter(
                x=self.df[date_col],
                y=self.df["Transfers"],
                mode='lines',
                name='Transfers',
                line=dict(color=self.config["visualization"]["colors"]["primary"])
            ))
        
        if "Discharges" in self.df.columns:
            fig.add_trace(go.Scatter(
                x=self.df[date_col],
                y=self.df["Discharges"],
                mode='lines',
                name='Discharges',
                line=dict(color=self.config["visualization"]["colors"]["secondary"])
            ))
        
        fig.update_layout(
            title="Daily Intake: Transfers vs Discharges",
            xaxis_title="Date",
            yaxis_title="Count",
            hovermode='x unified'
        )
        
        self.figures["daily_intake"] = fig
        
        if save:
            self._save_figure(fig, "daily_intake")
        
        return fig
    
    def plot_cpb_vs_hhs(self, save: bool = True) -> go.Figure:
        """
        Create CBP vs HHS comparison chart.
        
        Args:
            save: Whether to save the figure
            
        Returns:
            Plotly figure
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Creating CBP vs HHS chart")
        
        date_col = self.config["data"]["date_column"]
        
        fig = go.Figure()
        
        if "CBP Custody" in self.df.columns:
            fig.add_trace(go.Scatter(
                x=self.df[date_col],
                y=self.df["CBP Custody"],
                mode='lines',
                name='CBP Custody',
                line=dict(color=self.config["visualization"]["colors"]["primary"])
            ))
        
        if "HHS Care" in self.df.columns:
            fig.add_trace(go.Scatter(
                x=self.df[date_col],
                y=self.df["HHS Care"],
                mode='lines',
                name='HHS Care',
                line=dict(color=self.config["visualization"]["colors"]["tertiary"])
            ))
        
        fig.update_layout(
            title="CBP Custody vs HHS Care",
            xaxis_title="Date",
            yaxis_title="Count",
            hovermode='x unified'
        )
        
        self.figures["cbp_vs_hhs"] = fig
        
        if save:
            self._save_figure(fig, "cbp_vs_hhs")
        
        return fig
    
    def plot_system_load(self, save: bool = True) -> go.Figure:
        """
        Create total system load chart.
        
        Args:
            save: Whether to save the figure
            
        Returns:
            Plotly figure
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Creating system load chart")
        
        date_col = self.config["data"]["date_column"]
        
        fig = go.Figure()
        
        if "Total_System_Load" in self.df.columns:
            fig.add_trace(go.Scatter(
                x=self.df[date_col],
                y=self.df["Total_System_Load"],
                mode='lines',
                name='Total System Load',
                line=dict(color=self.config["visualization"]["colors"]["tertiary"]),
                fill='tozeroy'
            ))
        
        fig.update_layout(
            title="Total System Load Over Time",
            xaxis_title="Date",
            yaxis_title="Count",
            hovermode='x unified'
        )
        
        self.figures["system_load"] = fig
        
        if save:
            self._save_figure(fig, "system_load")
        
        return fig
    
    def plot_rolling_means(self, save: bool = True) -> go.Figure:
        """
        Create rolling means chart.
        
        Args:
            save: Whether to save the figure
            
        Returns:
            Plotly figure
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Creating rolling means chart")
        
        date_col = self.config["data"]["date_column"]
        
        fig = go.Figure()
        
        if "HHS_Care_Rolling_Mean_7d" in self.df.columns:
            fig.add_trace(go.Scatter(
                x=self.df[date_col],
                y=self.df["HHS_Care_Rolling_Mean_7d"],
                mode='lines',
                name='7-Day Rolling Mean',
                line=dict(color=self.config["visualization"]["colors"]["primary"])
            ))
        
        if "HHS_Care_Rolling_Mean_14d" in self.df.columns:
            fig.add_trace(go.Scatter(
                x=self.df[date_col],
                y=self.df["HHS_Care_Rolling_Mean_14d"],
                mode='lines',
                name='14-Day Rolling Mean',
                line=dict(color=self.config["visualization"]["colors"]["secondary"])
            ))
        
        if "HHS Care" in self.df.columns:
            fig.add_trace(go.Scatter(
                x=self.df[date_col],
                y=self.df["HHS Care"],
                mode='lines',
                name='Daily Values',
                line=dict(color=self.config["visualization"]["colors"]["tertiary"], dash='dot'),
                opacity=0.5
            ))
        
        fig.update_layout(
            title="Rolling Means: HHS Care",
            xaxis_title="Date",
            yaxis_title="Count",
            hovermode='x unified'
        )
        
        self.figures["rolling_means"] = fig
        
        if save:
            self._save_figure(fig, "rolling_means")
        
        return fig
    
    def plot_monthly_trends(self, save: bool = True) -> go.Figure:
        """
        Create monthly trends chart.
        
        Args:
            save: Whether to save the figure
            
        Returns:
            Plotly figure
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Creating monthly trends chart")
        
        date_col = self.config["data"]["date_column"]
        
        # Create monthly aggregation
        self.df["YearMonth"] = self.df[date_col].dt.to_period('M')
        monthly_data = self.df.groupby("YearMonth").agg({
            "Transfers": "sum",
            "Discharges": "sum",
            "HHS Care": "mean"
        }).reset_index()
        monthly_data["YearMonth"] = monthly_data["YearMonth"].astype(str)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Monthly Transfers", "Monthly Discharges", "Avg HHS Care", "Net Intake"),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        if "Transfers" in monthly_data.columns:
            fig.add_trace(
                go.Bar(x=monthly_data["YearMonth"], y=monthly_data["Transfers"], name="Transfers"),
                row=1, col=1
            )
        
        if "Discharges" in monthly_data.columns:
            fig.add_trace(
                go.Bar(x=monthly_data["YearMonth"], y=monthly_data["Discharges"], name="Discharges"),
                row=1, col=2
            )
        
        if "HHS Care" in monthly_data.columns:
            fig.add_trace(
                go.Scatter(x=monthly_data["YearMonth"], y=monthly_data["HHS Care"], 
                          mode='lines+markers', name="Avg HHS Care"),
                row=2, col=1
            )
        
        if "Transfers" in monthly_data.columns and "Discharges" in monthly_data.columns:
            monthly_data["Net_Intake"] = monthly_data["Transfers"] - monthly_data["Discharges"]
            fig.add_trace(
                go.Bar(x=monthly_data["YearMonth"], y=monthly_data["Net_Intake"], name="Net Intake"),
                row=2, col=2
            )
        
        fig.update_layout(
            title_text="Monthly Trends Analysis",
            showlegend=False,
            height=600
        )
        
        self.figures["monthly_trends"] = fig
        
        if save:
            self._save_figure(fig, "monthly_trends")
        
        return fig
    
    def plot_distribution(self, save: bool = True) -> go.Figure:
        """
        Create distribution plots for key metrics.
        
        Args:
            save: Whether to save the figure
            
        Returns:
            Plotly figure
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Creating distribution plots")
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("HHS Care Distribution", "Transfers Distribution", 
                          "Discharges Distribution", "Net Intake Distribution")
        )
        
        if "HHS Care" in self.df.columns:
            fig.add_trace(
                go.Histogram(x=self.df["HHS Care"], name="HHS Care", nbinsx=30),
                row=1, col=1
            )
        
        if "Transfers" in self.df.columns:
            fig.add_trace(
                go.Histogram(x=self.df["Transfers"], name="Transfers", nbinsx=30),
                row=1, col=2
            )
        
        if "Discharges" in self.df.columns:
            fig.add_trace(
                go.Histogram(x=self.df["Discharges"], name="Discharges", nbinsx=30),
                row=2, col=1
            )
        
        if "Net_Daily_Intake" in self.df.columns:
            fig.add_trace(
                go.Histogram(x=self.df["Net_Daily_Intake"], name="Net Intake", nbinsx=30),
                row=2, col=2
            )
        
        fig.update_layout(
            title_text="Distribution Analysis",
            showlegend=False,
            height=600
        )
        
        self.figures["distribution"] = fig
        
        if save:
            self._save_figure(fig, "distribution")
        
        return fig
    
    def plot_correlation_heatmap(self, save: bool = True) -> go.Figure:
        """
        Create correlation heatmap.
        
        Args:
            save: Whether to save the figure
            
        Returns:
            Plotly figure
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Creating correlation heatmap")
        
        # Select numeric columns
        numeric_cols = ["CBP Custody", "Transfers", "HHS Care", "Discharges", 
                       "Total_System_Load", "Net_Daily_Intake"]
        available_cols = [col for col in numeric_cols if col in self.df.columns]
        
        if len(available_cols) < 2:
            self.logger.warning("Not enough numeric columns for correlation heatmap")
            return go.Figure()
        
        corr_matrix = self.df[available_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate="%{text}",
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title="Correlation Heatmap",
            width=600,
            height=600
        )
        
        self.figures["correlation_heatmap"] = fig
        
        if save:
            self._save_figure(fig, "correlation_heatmap")
        
        return fig
    
    def plot_boxplots(self, save: bool = True) -> go.Figure:
        """
        Create boxplots for key metrics.
        
        Args:
            save: Whether to save the figure
            
        Returns:
            Plotly figure
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Creating boxplots")
        
        numeric_cols = ["CBP Custody", "Transfers", "HHS Care", "Discharges"]
        available_cols = [col for col in numeric_cols if col in self.df.columns]
        
        fig = go.Figure()
        
        for col in available_cols:
            fig.add_trace(go.Box(
                y=self.df[col],
                name=col,
                boxpoints='outliers'
            ))
        
        fig.update_layout(
            title="Boxplot Analysis",
            yaxis_title="Count",
            showlegend=False
        )
        
        self.figures["boxplots"] = fig
        
        if save:
            self._save_figure(fig, "boxplots")
        
        return fig
    
    def plot_seasonal_decomposition(self, save: bool = True) -> go.Figure:
        """
        Create seasonal decomposition plot.
        
        Args:
            save: Whether to save the figure
            
        Returns:
            Plotly figure
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.logger.info("Creating seasonal decomposition")
        
        try:
            from statsmodels.tsa.seasonal import seasonal_decompose
            
            if "HHS Care" not in self.df.columns:
                self.logger.warning("HHS Care column not found for seasonal decomposition")
                return go.Figure()
            
            # Perform seasonal decomposition
            date_col = self.config["data"]["date_column"]
            df_ts = self.df.set_index(date_col)
            
            decomposition = seasonal_decompose(
                df_ts["HHS Care"],
                model='additive',
                period=7  # Weekly seasonality
            )
            
            fig = make_subplots(
                rows=4, cols=1,
                subplot_titles=("Original", "Trend", "Seasonal", "Residual"),
                vertical_spacing=0.05
            )
            
            fig.add_trace(
                go.Scatter(x=df_ts.index, y=decomposition.observed, name="Original"),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=df_ts.index, y=decomposition.trend, name="Trend"),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=df_ts.index, y=decomposition.seasonal, name="Seasonal"),
                row=3, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=df_ts.index, y=decomposition.resid, name="Residual"),
                row=4, col=1
            )
            
            fig.update_layout(
                title_text="Seasonal Decomposition: HHS Care",
                height=800,
                showlegend=False
            )
            
            self.figures["seasonal_decomposition"] = fig
            
            if save:
                self._save_figure(fig, "seasonal_decomposition")
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error in seasonal decomposition: {str(e)}")
            return go.Figure()
    
    def create_all_plots(self, save: bool = True) -> Dict[str, go.Figure]:
        """
        Create all visualization plots.
        
        Args:
            save: Whether to save the figures
            
        Returns:
            Dictionary of all figures
        """
        self.logger.info("Creating all visualization plots")
        
        self.plot_daily_intake(save)
        self.plot_cpb_vs_hhs(save)
        self.plot_system_load(save)
        self.plot_rolling_means(save)
        self.plot_monthly_trends(save)
        self.plot_distribution(save)
        self.plot_correlation_heatmap(save)
        self.plot_boxplots(save)
        self.plot_seasonal_decomposition(save)
        
        self.logger.info(f"Created {len(self.figures)} visualization plots")
        
        return self.figures
    
    def _save_figure(self, fig: go.Figure, name: str) -> None:
        """
        Save figure to file.
        
        Args:
            fig: Plotly figure
            name: Figure name
        """
        output_dir = Path("output/plots")
        ensure_directory(str(output_dir))
        
        output_path = output_dir / f"{name}.png"
        fig.write_image(str(output_path), 
                       width=1200, 
                       height=self.config["visualization"]["figure_size"]["height"] * 100,
                       scale=2)
        
        self.logger.info(f"Saved figure: {output_path}")


def main():
    """
    Main function to run visualization pipeline.
    """
    visualizer = Visualizer()
    visualizer.load_data()
    figures = visualizer.create_all_plots()
    
    print(f"Visualization completed. Created {len(figures)} plots.")
    print("Plots saved to: output/plots/")


if __name__ == "__main__":
    main()

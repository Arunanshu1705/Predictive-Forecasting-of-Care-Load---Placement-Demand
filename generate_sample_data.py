"""
Sample Data Generator

This module generates a realistic sample dataset for the HHS UAC Program analytics.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path


def generate_sample_data(start_date: str = "2023-01-01", 
                        end_date: str = "2024-12-31",
                        output_path: str = "data/raw/HHS_Unaccompanied_Alien_Children_Program.csv"):
    """
    Generate sample HHS UAC Program data.
    
    Args:
        start_date: Start date for data generation
        end_date: End date for data generation
        output_path: Output file path
    """
    print(f"Generating sample data from {start_date} to {end_date}")
    
    # Create date range
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    n_days = len(dates)
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate realistic data with trends and seasonality
    data = []
    
    # Initial values
    cbp_custody = 5000
    hhs_care = 8000
    
    for i, date in enumerate(dates):
        # Add seasonal patterns (higher in spring/summer)
        month = date.month
        seasonal_factor = 1.0 + 0.3 * np.sin(2 * np.pi * (month - 3) / 12)
        
        # Add trend (gradual increase over time)
        trend_factor = 1.0 + 0.0005 * i
        
        # Add weekly patterns (higher on weekdays)
        day_of_week = date.dayofweek
        weekly_factor = 1.0 + 0.1 * (1 if day_of_week < 5 else -1)
        
        # Generate daily values with noise
        transfers = int(np.random.normal(400 * seasonal_factor * trend_factor * weekly_factor, 50))
        transfers = max(100, min(800, transfers))  # Clamp to reasonable range
        
        discharges = int(np.random.normal(350 * seasonal_factor * trend_factor * weekly_factor, 40))
        discharges = max(100, min(700, discharges))
        
        # Update custody and care values
        cbp_custody = max(2000, cbp_custody + transfers - int(transfers * 0.8) + np.random.randint(-50, 50))
        hhs_care = max(5000, hhs_care + transfers - discharges + np.random.randint(-30, 30))
        
        # Ensure transfers <= CBP custody and discharges <= HHS care
        transfers = min(transfers, cbp_custody)
        discharges = min(discharges, hhs_care)
        
        data.append({
            "Date": date.strftime("%Y-%m-%d"),
            "CBP Custody": cbp_custody,
            "Transfers": transfers,
            "HHS Care": hhs_care,
            "Discharges": discharges
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    
    print(f"Sample data generated: {len(df)} rows")
    print(f"Output saved to: {output_path}")
    print(f"\nData summary:")
    print(df.describe())
    
    return df


if __name__ == "__main__":
    # Generate 2 years of sample data
    generate_sample_data(
        start_date="2023-01-01",
        end_date="2024-12-31",
        output_path="data/raw/HHS_Unaccompanied_Alien_Children_Program.csv"
    )

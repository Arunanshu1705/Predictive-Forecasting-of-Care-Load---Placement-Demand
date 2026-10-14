"""
Backend Utilities Module

This module provides utility functions for the backend API and analytics.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except UnicodeDecodeError:
        with open(config_file, 'r', encoding='latin1') as f:
            config = yaml.safe_load(f)
    
    return config


def load_env() -> None:
    """
    Load environment variables from .env file.
    """
    env_file = Path(".env")
    
    if env_file.exists():
        try:
            load_dotenv(env_file)
        except Exception:
            # Ignore encoding issues with .env file
            pass


def get_env_var(key: str, default: Optional[str] = None) -> str:
    """
    Get environment variable with optional default.
    
    Args:
        key: Environment variable key
        default: Default value if not found
        
    Returns:
        Environment variable value
    """
    value = os.getenv(key, default)
    
    if value is None:
        raise ValueError(f"Environment variable {key} not set and no default provided")
    
    return value


def ensure_directory(path: str) -> Path:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_data_path(config: Dict[str, Any], data_type: str = "raw") -> str:
    """
    Get data path from configuration.
    
    Args:
        config: Configuration dictionary
        data_type: Type of data ('raw' or 'processed')
        
    Returns:
        Data file path
    """
    if data_type == "raw":
        return config["data"]["raw_path"]
    elif data_type == "processed":
        return config["data"]["processed_path"]
    else:
        raise ValueError(f"Invalid data type: {data_type}")


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration structure.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if valid, raises exception if invalid
    """
    required_sections = ["data", "preprocessing", "validation", "features", "kpi"]
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    return True


def format_number(value: float, decimals: int = 2) -> str:
    """
    Format number for display.
    
    Args:
        value: Numeric value
        decimals: Number of decimal places
        
    Returns:
        Formatted string
    """
    if value is None or (isinstance(value, float) and (value != value)):  # Check for NaN
        return "N/A"
    
    return f"{value:,.{decimals}f}"


def calculate_percentage(numerator: float, denominator: float) -> float:
    """
    Calculate percentage safely.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        
    Returns:
        Percentage value (0 if denominator is 0)
    """
    if denominator == 0:
        return 0.0
    
    return (numerator / denominator) * 100


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safe division with default value for division by zero.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if division by zero
        
    Returns:
        Division result or default
    """
    if denominator == 0:
        return default
    
    return numerator / denominator

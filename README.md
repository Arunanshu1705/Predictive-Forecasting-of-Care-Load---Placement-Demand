# System Capacity & Care Load Analytics for Unaccompanied Children

A comprehensive healthcare analytics system for monitoring and analyzing the operational capacity of the U.S. Department of Health and Human Services (HHS) Unaccompanied Alien Children (UAC) Program.

## 📋 Project Overview

This project provides a complete, production-ready analytics platform that monitors the complete care pipeline from CBP intake to HHS discharge, identifies system pressure, quantifies care load, calculates operational KPIs, and presents insights through an interactive Streamlit dashboard.

### Key Features

- **Automated Data Pipeline**: End-to-end data processing, validation, and feature engineering
- **Advanced Analytics**: Capacity stress detection, backlog analysis, pressure windows, and growth trends
- **Interactive Dashboard**: Real-time Streamlit dashboard with multiple visualization pages
- **REST API**: FastAPI backend for programmatic access to analytics
- **Report Generation**: Automated PDF report generation with key findings
- **Docker Support**: Containerized deployment with Docker and Docker Compose
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## 🏗️ Architecture

```
System_Capacity_Analytics/
│
├── app/                          # Streamlit Dashboard
│   ├── streamlit_app.py         # Main dashboard application
│   ├── pages/                    # Dashboard pages
│   │   ├── overview.py           # System overview
│   │   ├── capacity.py           # Capacity analysis
│   │   ├── trends.py             # Trend analysis
│   │   ├── backlog.py            # Pressure analysis
│   │   ├── kpis.py               # KPI details
│   │   └── insights.py           # Automated insights
│
├── backend/                      # Backend Services
│   ├── api.py                    # FastAPI REST API
│   ├── analytics.py              # Healthcare analytics
│   └── utils.py                  # Backend utilities
│
├── src/                          # Core Processing Modules
│   ├── preprocessing.py          # Data ingestion & cleaning
│   ├── validation.py             # Data validation
│   ├── feature_engineering.py    # Feature engineering
│   ├── kpi.py                    # KPI calculations
│   ├── visualization.py          # Chart generation
│   ├── report_generator.py       # PDF report generation
│   └── logger.py                 # Logging configuration
│
├── data/                         # Data Storage
│   ├── raw/                      # Raw data files
│   └── processed/                # Processed data files
│
├── reports/                      # Generated Reports
├── output/                       # Output files (exports, plots)
├── notebooks/                    # Jupyter notebooks
│
├── config.yaml                   # Application configuration
├── .env                          # Environment variables
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose configuration
├── main.py                       # Main entry point
└── README.md                     # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Docker (optional, for containerized deployment)

### Local Installation

1. **Clone the repository** (or navigate to the project directory):
```bash
cd "Predictive Forecasting of Care Load & Placement Demand"
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Prepare the data**:
```bash
# Generate sample data (if you don't have the actual dataset)
python generate_sample_data.py

# Or place your CSV file at: data/raw/HHS_Unaccompanied_Alien_Children_Program.csv
```

4. **Configure the application**:
```bash
# Edit config.yaml to customize settings
# Edit .env for environment-specific variables
```

### Docker Installation

1. **Build and run with Docker Compose**:
```bash
docker-compose up -d
```

2. **Access the dashboard**:
- Streamlit Dashboard: http://localhost:8501
- FastAPI Backend: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📊 Usage

### Running the Complete Pipeline

Run the entire analytics pipeline from command line:

```bash
# Full pipeline (preprocessing, validation, analytics, visualization, reporting)
python main.py --mode full

# Individual components
python main.py --mode preprocessing
python main.py --mode validation
python main.py --mode analytics
```

### Running the Streamlit Dashboard

```bash
streamlit run app/streamlit_app.py
```

The dashboard will be available at http://localhost:8501

### Running the FastAPI Backend

```bash
# Start the API server
python -m uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

API documentation will be available at http://localhost:8000/docs

### Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📈 Dashboard Pages

### 1. Overview
- System status and overall assessment
- Key performance indicators at a glance
- Extreme values and recent data preview
- Quick analytics summary

### 2. Capacity
- CBP vs HHS comparison
- Total system load analysis
- Capacity stress detection
- High load period identification
- Moving average analysis

### 3. Trends
- Daily, weekly, and monthly trend analysis
- Net intake trends
- Growth patterns
- Variance analysis
- Granularity selector for different time periods

### 4. Pressure Analysis
- Backlog analysis and trends
- Pressure windows (7-day, 14-day, 30-day)
- Net intake pressure visualization
- Discharge offset analysis
- Pressure pattern identification

### 5. KPIs
- Detailed KPI cards with explanations
- Interactive KPI comparison charts
- Export options (JSON, CSV)
- Historical KPI data

### 6. Insights
- Automated insights based on analytics
- Data quality assessment
- Recommended action items
- Summary of key findings

## 🔧 Configuration

### config.yaml

Main configuration file for the application:

```yaml
# Data Configuration
data:
  raw_path: "data/raw/HHS_Unaccompanied_Alien_Children_Program.csv"
  processed_path: "data/processed/processed_data.csv"
  date_column: "Date"

# Validation thresholds
validation:
  anomaly_thresholds:
    daily_change_percent: 50
    zero_consecutive_days: 7

# KPI thresholds
kpi:
  pressure_thresholds:
    high_load: 10000
    critical_load: 15000
```

### .env

Environment variables for deployment:

```env
API_HOST=0.0.0.0
API_PORT=8000
STREAMLIT_SERVER_PORT=8501
LOG_LEVEL=INFO
```

## 📡 API Endpoints

### Health & Status
- `GET /` - API information
- `GET /health` - Health check
- `POST /refresh` - Refresh data and recalculate

### Data & Analytics
- `GET /kpis` - Get current KPIs
- `GET /analytics` - Get healthcare analytics
- `GET /capacity` - Get capacity analysis
- `GET /trends` - Get trend analysis
- `GET /backlog` - Get backlog analysis
- `GET /summary` - Get comprehensive summary
- `GET /validation` - Get validation results

### Reports & Exports
- `GET /report/generate` - Generate PDF report
- `GET /report/download` - Download latest report
- `GET /export/csv` - Export data as CSV
- `GET /export/excel` - Export data as Excel

## 🧪 Testing

Run the complete pipeline to test the application:

```bash
# Generate sample data
python generate_sample_data.py

# Run full pipeline
python main.py --mode full

# Start dashboard
streamlit run app/streamlit_app.py
```

## 📝 Key Performance Indicators

The system calculates the following KPIs:

### Current Status
- **Total Children Under Care**: Latest HHS Care count
- **Average System Load**: Mean of total system load

### Daily Averages
- **Average Daily Intake**: Mean of daily transfers
- **Average Daily Discharges**: Mean of daily discharges
- **Average CBP Load**: Mean of CBP custody
- **Average HHS Load**: Mean of HHS care

### Pressure Indicators
- **Net Intake Pressure**: Mean of (Transfers - Discharges)
- **Care Load Volatility Index**: Std dev / mean of HHS Care
- **Backlog Accumulation Rate**: Daily backlog change rate
- **Discharge Offset Ratio**: Discharges / Transfers

### Extreme Values
- **Peak Load Day**: Maximum system load day
- **Lowest Load Day**: Minimum system load day
- **Highest Intake**: Maximum transfers day
- **Highest Discharge**: Maximum discharges day

## 🔍 Analytics Features

### Capacity Stress Detection
- Identifies periods when system load exceeds thresholds
- Calculates stress duration and frequency
- Provides early warning for capacity issues

### Backlog Analysis
- Tracks backlog accumulation over time
- Identifies increasing/decreasing trends
- Calculates accumulation rates

### Pressure Windows
- Multi-timeframe pressure analysis (7, 14, 30 days)
- Identifies high-pressure periods
- Provides context for operational decisions

### Growth Trend Analysis
- Tracks population growth patterns
- Identifies accelerating/decelerating growth
- Projects future capacity needs

### Moving Average Signals
- Technical analysis of trends
- Bullish/bearish signal identification
- Crossover detection

### Variance Analysis
- Operational stability assessment
- High volatility period detection
- Risk identification

## 📄 Report Generation

The system generates comprehensive PDF reports including:

- Executive Summary
- Dataset Overview
- Data Validation Report
- KPI Analysis
- Healthcare Analytics
- Recommendations
- Conclusion

Reports can be generated via:
- Dashboard button
- API endpoint: `GET /report/generate`
- Command line: `python main.py --mode full`

## 🛠️ Development

### Adding New Features

1. **New Analytics**: Add methods to `backend/analytics.py`
2. **New KPIs**: Add calculations to `src/kpi.py`
3. **New Visualizations**: Add charts to `src/visualization.py`
4. **New Dashboard Pages**: Create new page in `app/pages/`

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Include docstrings for all functions and classes
- Use object-oriented design where appropriate
- Handle exceptions gracefully

### Logging

Logs are stored in the `logs/` directory:
- `app.log` - Application logs
- `main.log` - Pipeline execution logs
- `preprocessing.log` - Data preprocessing logs
- `validation.log` - Data validation logs
- `analytics.log` - Analytics logs

## 🐛 Troubleshooting

### Common Issues

**Issue**: Module not found errors
- **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

**Issue**: Data file not found
- **Solution**: Ensure CSV file is at `data/raw/HHS_Unaccompanied_Alien_Children_Program.csv` or generate sample data with `python generate_sample_data.py`

**Issue**: Port already in use
- **Solution**: Change port in `.env` file or stop the conflicting service

**Issue**: Docker build fails
- **Solution**: Ensure Docker is running and you have sufficient disk space

## 🔄 Future Work

- [ ] Machine learning models for capacity forecasting
- [ ] Real-time data streaming integration
- [ ] Advanced anomaly detection
- [ ] Multi-region analysis
- [ ] User authentication and authorization
- [ ] Email/SMS alerts for critical events
- [ ] Mobile application
- [ ] Additional data sources integration

## 📄 License

This project is for educational and analytical purposes.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues, questions, or suggestions:
- Create an issue in the repository
- Check existing documentation
- Review logs in the `logs/` directory

## 🙏 Acknowledgments

This project was developed to provide analytical insights into the HHS Unaccompanied Alien Children Program operations, with the goal of supporting data-driven decision-making and improving care outcomes.

---

**Built with Python, Streamlit, FastAPI, and modern data science tools.**

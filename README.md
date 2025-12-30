# Fulfillment KPI Dashboard

An interactive analytics dashboard built with Python and Streamlit that simulates fulfillment operations across multiple Michigan distribution centers.

## Overview
This project models end to end fulfillment performance using realistic operational metrics commonly used in supply chain and operations analytics. The dashboard is designed to resemble an internal decision support tool used to monitor performance and identify inefficiencies.

## Key Features
- Interactive filtering by fulfillment center and date range  
- KPI summary cards with target comparisons  
- Fulfillment center level benchmarking  
- Daily trend analysis for operational metrics  
- Downloadable filtered dataset  
- Clean dark themed interface  

## Technologies Used
- Python  
- Pandas  
- Plotly  
- Streamlit  

## Data and Logic
The dataset is programmatically generated to simulate realistic fulfillment behavior across Michigan based centers. Metrics are calculated using industry aligned business logic to ensure consistency and meaningful trends.

Fulfillment centers included:
- DTW1  
- DET2  
- DET3  
- DTW5  

## How to Run Locally
1. Clone the repository  
2. Install dependencies  
3. Launch the Streamlit application  

streamlit run app.py


## Future Improvements
- Integration with real world datasets  
- User authentication and saved views  
- Exportable executive reports  

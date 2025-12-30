# Fulfillment KPI Dashboard

An interactive fulfillment analytics dashboard built with Python and Streamlit to simulate Amazon style operations across Michigan fulfillment centers.

## Overview
This project models end to end fulfillment performance using realistic operational metrics such as:
- Order cycle time
- On time shipment rate
- Order accuracy
- Backorder rate

The dashboard is designed to resemble an internal operations tool used by supply chain and analytics teams.

## Key Features
- Interactive filters by fulfillment center and date range
- KPI cards with performance deltas vs targets
- Center level performance comparison
- Daily trend analysis for cycle time and accuracy
- Downloadable filtered dataset

## Technologies Used
- Python
- Pandas
- Plotly
- Streamlit

## Data
The dataset is programmatically generated to simulate realistic fulfillment behavior across Michigan based distribution centers:
- DTW1
- DET2
- DET3
- DTW5

Metrics are calculated using business logic aligned with real world fulfillment definitions.

## Screenshot
![Dashboard Screenshot](outputs/dashboard_screenshot.png)

## How to Run Locally

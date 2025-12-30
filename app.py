import os
import random
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Michigan Fulfillment KPI Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styling (simple, professional)
st.markdown(
    """
    <style>
      .block-container {padding-top: 2rem; padding-bottom: 2rem;}
      .small-muted {color: rgba(255,255,255,0.70); font-size: 0.92rem;}
      .section-title {font-size: 1.15rem; font-weight: 700; margin-top: 0.25rem;}
      .card-note {color: rgba(255,255,255,0.75); font-size: 0.90rem;}
    </style>
    """,
    unsafe_allow_html=True
)

# Data generation (fallback)
def generate_simulated_data(seed=2025, num_orders=10000):
    random.seed(seed)

    start_date = datetime(2024, 12, 1)
    date_span_days = 16

    centers = ["DTW1", "DET2", "DET3", "DTW5"]
    center_weights = [0.35, 0.20, 0.25, 0.20]

    rows = []

    for i in range(1, num_orders + 1):
        order_id = 1000 + i

        order_date = start_date + timedelta(days=random.randint(0, date_span_days - 1))

        promised_days = random.choice([1, 2, 2, 2, 3])
        promised_ship_date = order_date + timedelta(days=promised_days)

        ship_delay = random.choices(
            population=[0, 1, 2, 3, 4],
            weights=[0.20, 0.40, 0.28, 0.09, 0.03],
            k=1
        )[0]
        ship_date = order_date + timedelta(days=ship_delay)

        pick_time = random.randint(6, 28)
        pack_time = random.randint(3, 16)

        items_ordered = random.choice([1, 1, 2, 2, 2, 3, 4, 5])

        backorder_flag = "Yes" if random.random() < 0.06 else "No"

        if backorder_flag == "Yes":
            items_shipped_correctly = max(0, items_ordered - random.choice([1, 1, 2]))
        else:
            items_shipped_correctly = items_ordered if random.random() > 0.02 else max(0, items_ordered - 1)

        fulfillment_center = random.choices(centers, weights=center_weights, k=1)[0]

        rows.append({
            "order_id": order_id,
            "order_date": order_date,
            "ship_date": ship_date,
            "promised_ship_date": promised_ship_date,
            "pick_time_minutes": pick_time,
            "pack_time_minutes": pack_time,
            "items_ordered": items_ordered,
            "items_shipped_correctly": items_shipped_correctly,
            "backorder_flag": backorder_flag,
            "fulfillment_center": fulfillment_center
        })

    df = pd.DataFrame(rows)

    df["cycle_time_days"] = (df["ship_date"] - df["order_date"]).dt.days
    df["cycle_time_days"] = df["cycle_time_days"].clip(lower=0)
    df["on_time_flag"] = df["ship_date"] <= df["promised_ship_date"]
    df["accuracy_flag"] = (df["items_shipped_correctly"] == df["items_ordered"]) & (df["backorder_flag"] == "No")

    return df

@st.cache_data
def load_data():
    csv_path = os.path.join("data", "simulated_fulfillment_orders.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df["order_date"] = pd.to_datetime(df["order_date"])
        df["ship_date"] = pd.to_datetime(df["ship_date"])
        df["promised_ship_date"] = pd.to_datetime(df["promised_ship_date"])

        if "cycle_time_days" not in df.columns:
            df["cycle_time_days"] = (df["ship_date"] - df["order_date"]).dt.days
            df["cycle_time_days"] = df["cycle_time_days"].clip(lower=0)

        if "on_time_flag" not in df.columns:
            df["on_time_flag"] = df["ship_date"] <= df["promised_ship_date"]

        if "accuracy_flag" not in df.columns:
            df["accuracy_flag"] = (df["items_shipped_correctly"] == df["items_ordered"]) & (df["backorder_flag"] == "No")

        return df

    return generate_simulated_data(seed=2025, num_orders=10000)

def compute_kpis(df):
    n = int(len(df))
    if n == 0:
        return {"total_orders": 0, "avg_cycle": 0.0, "on_time": 0.0, "accuracy": 0.0, "backorder": 0.0}

    return {
        "total_orders": n,
        "avg_cycle": float(df["cycle_time_days"].mean()),
        "on_time": float(df["on_time_flag"].mean() * 100),
        "accuracy": float(df["accuracy_flag"].mean() * 100),
        "backorder": float((df["backorder_flag"] == "Yes").mean() * 100),
    }

def daily_table(df):
    daily = df.groupby(df["order_date"].dt.date).agg(
        orders=("order_id", "count"),
        avg_cycle_time=("cycle_time_days", "mean"),
        on_time_rate=("on_time_flag", "mean"),
        accuracy_rate=("accuracy_flag", "mean")
    ).reset_index().rename(columns={"order_date": "date"})

    daily["date"] = pd.to_datetime(daily["date"])
    daily["on_time_rate_pct"] = daily["on_time_rate"] * 100
    daily["accuracy_rate_pct"] = daily["accuracy_rate"] * 100
    return daily

def by_center_table(df):
    by_center = df.groupby("fulfillment_center").agg(
        orders=("order_id", "count"),
        avg_cycle_time=("cycle_time_days", "mean"),
        on_time_rate=("on_time_flag", "mean"),
        accuracy_rate=("accuracy_flag", "mean"),
        backorder_rate=("backorder_flag", lambda s: (s == "Yes").mean())
    ).reset_index()

    by_center["on_time_rate_pct"] = by_center["on_time_rate"] * 100
    by_center["accuracy_rate_pct"] = by_center["accuracy_rate"] * 100
    by_center["backorder_rate_pct"] = by_center["backorder_rate"] * 100
    return by_center

# Load base data
df = load_data()

# Header
st.markdown("## Michigan Fulfillment KPI Dashboard")
st.markdown(
    '<div class="small-muted">Simulated Amazon style operations analytics across Michigan fulfillment centers. Use filters to explore performance.</div>',
    unsafe_allow_html=True
)

# Sidebar filters
with st.sidebar:
    st.markdown("### Filters")

    centers_all = sorted(df["fulfillment_center"].unique().tolist())
    selected_centers = st.multiselect("Fulfillment centers", centers_all, default=centers_all)

    min_date = df["order_date"].min().date()
    max_date = df["order_date"].max().date()
    date_range = st.date_input("Order date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    st.markdown("### Targets")
    target_on_time = st.slider("On time target percent", 80, 99, 95)
    target_accuracy = st.slider("Accuracy target percent", 80, 99, 98)

    st.markdown("### Display")
    show_data = st.checkbox("Show data preview", value=False)

# Normalize date inputs
if isinstance(date_range, tuple) and len(date_range) == 2:
    d0, d1 = date_range
else:
    d0, d1 = min_date, max_date

# Apply filters
filtered = df[
    (df["fulfillment_center"].isin(selected_centers))
    & (df["order_date"].dt.date >= d0)
    & (df["order_date"].dt.date <= d1)
].copy()

# KPI row with deltas
k = compute_kpis(filtered)

delta_on_time = k["on_time"] - float(target_on_time)
delta_accuracy = k["accuracy"] - float(target_accuracy)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Orders", f"{k['total_orders']:,}")
c2.metric("Avg Cycle Time days", f"{k['avg_cycle']:.2f}")
c3.metric("On Time Percent", f"{k['on_time']:.2f}", f"{delta_on_time:.2f} vs target")
c4.metric("Accuracy Percent", f"{k['accuracy']:.2f}", f"{delta_accuracy:.2f} vs target")
c5.metric("Backorder Percent", f"{k['backorder']:.2f}")

st.markdown(
    '<div class="card-note">Interpretation tip: backorders usually reduce both on time performance and accuracy, so watch them together.</div>',
    unsafe_allow_html=True
)

st.divider()

# Tabs
tab_overview, tab_centers, tab_trends = st.tabs(["Overview", "Centers", "Trends"])

# Prepare tables once
daily = daily_table(filtered) if len(filtered) else pd.DataFrame()
by_center = by_center_table(filtered) if len(filtered) else pd.DataFrame()

# Plotly theme choices
px.defaults.template = "plotly_dark"

with tab_overview:
    st.markdown('<div class="section-title">Executive Summary</div>', unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        if len(by_center):
            fig_vol = px.bar(
                by_center,
                x="fulfillment_center",
                y="orders",
                text="orders",
                title="Order Volume by Fulfillment Center"
            )
            fig_vol.update_traces(textposition="outside", cliponaxis=False)
            fig_vol.update_layout(xaxis_title="Fulfillment Center", yaxis_title="Orders")
            st.plotly_chart(fig_vol, use_container_width=True)
        else:
            st.info("No data for current filters.")

    with right:
        if len(by_center):
            fig_ot = px.bar(
                by_center,
                x="fulfillment_center",
                y="on_time_rate_pct",
                title="On Time Shipment Rate by Fulfillment Center"
            )
            fig_ot.add_hline(y=target_on_time, line_dash="dash", annotation_text=f"Target {target_on_time} percent")
            fig_ot.update_layout(xaxis_title="Fulfillment Center", yaxis_title="Percent", yaxis_range=[0, 100])
            st.plotly_chart(fig_ot, use_container_width=True)
        else:
            st.info("No data for current filters.")

with tab_centers:
    st.markdown('<div class="section-title">Center Scorecard</div>', unsafe_allow_html=True)

    if len(by_center):
        scorecard = by_center[[
            "fulfillment_center",
            "orders",
            "avg_cycle_time",
            "on_time_rate_pct",
            "accuracy_rate_pct",
            "backorder_rate_pct"
        ]].copy()

        scorecard = scorecard.rename(columns={
            "fulfillment_center": "Center",
            "orders": "Orders",
            "avg_cycle_time": "Avg Cycle Days",
            "on_time_rate_pct": "On Time Percent",
            "accuracy_rate_pct": "Accuracy Percent",
            "backorder_rate_pct": "Backorder Percent"
        })

        st.dataframe(scorecard, use_container_width=True)

        colA, colB = st.columns(2)

        with colA:
            fig_acc = px.bar(
                by_center,
                x="fulfillment_center",
                y="accuracy_rate_pct",
                title="Accuracy Rate by Fulfillment Center"
            )
            fig_acc.add_hline(y=target_accuracy, line_dash="dash", annotation_text=f"Target {target_accuracy} percent")
            fig_acc.update_layout(xaxis_title="Fulfillment Center", yaxis_title="Percent", yaxis_range=[0, 100])
            st.plotly_chart(fig_acc, use_container_width=True)

        with colB:
            fig_bo = px.bar(
                by_center,
                x="fulfillment_center",
                y="backorder_rate_pct",
                title="Backorder Rate by Fulfillment Center"
            )
            fig_bo.update_layout(xaxis_title="Fulfillment Center", yaxis_title="Percent", yaxis_range=[0, max(5, float(by_center["backorder_rate_pct"].max()) + 2)])
            st.plotly_chart(fig_bo, use_container_width=True)
    else:
        st.info("No data for current filters.")

with tab_trends:
    st.markdown('<div class="section-title">Trends Over Time</div>', unsafe_allow_html=True)

    left2, right2 = st.columns(2)

    with left2:
        if len(daily):
            fig_cycle = px.line(
                daily,
                x="date",
                y="avg_cycle_time",
                title="Daily Average Cycle Time Trend"
            )
            fig_cycle.update_layout(xaxis_title="Order Date", yaxis_title="Days")
            st.plotly_chart(fig_cycle, use_container_width=True)
        else:
            st.info("No data for current filters.")

    with right2:
        if len(daily):
            fig_acc_tr = px.line(
                daily,
                x="date",
                y="accuracy_rate_pct",
                title="Daily Order Accuracy Trend"
            )
            fig_acc_tr.add_hline(y=target_accuracy, line_dash="dash", annotation_text=f"Target {target_accuracy} percent")
            fig_acc_tr.update_layout(xaxis_title="Order Date", yaxis_title="Percent", yaxis_range=[0, 100])
            st.plotly_chart(fig_acc_tr, use_container_width=True)
        else:
            st.info("No data for current filters.")

    if len(daily):
        fig_ot_tr = px.line(
            daily,
            x="date",
            y="on_time_rate_pct",
            title="Daily On Time Shipment Trend"
        )
        fig_ot_tr.add_hline(y=target_on_time, line_dash="dash", annotation_text=f"Target {target_on_time} percent")
        fig_ot_tr.update_layout(xaxis_title="Order Date", yaxis_title="Percent", yaxis_range=[0, 100])
        st.plotly_chart(fig_ot_tr, use_container_width=True)

st.divider()

# Data preview and download
if show_data:
    st.markdown("### Data preview")
    st.dataframe(filtered.head(75), use_container_width=True)

st.download_button(
    label="Download filtered data as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_fulfillment_data.csv",
    mime="text/csv",
)

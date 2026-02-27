import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src.data_loader import load_all_tables
from src.filters import apply_global_filters

# -------------------------------
# PAGE TITLE
# -------------------------------
st.title(":green[Driver Performance 👨‍✈️]")

# -------------------------------
# LOAD + FILTER DATA
# -------------------------------
data = load_all_tables()
data = apply_global_filters(data)

drivers = data["drivers"]
driver_metrics = data["driver_monthly_metrics"]

# -------------------------------
# KPI CALCULATIONS
# -------------------------------

total_drivers = len(drivers)
active_drivers = len(drivers[drivers["employment_status"] == "Active"])
terminated_drivers = len(drivers[drivers["employment_status"] == "Terminated"])

# Aggregate driver metrics for total revenue, trips, miles
total_revenue = driver_metrics["total_revenue"].sum()
total_trips = driver_metrics["trips_completed"].sum()
total_miles = driver_metrics["total_miles"].sum()

# Top driver by revenue
driver_revenue = driver_metrics.groupby("driver_id")["total_revenue"].sum()
top_driver_id = driver_revenue.idxmax() if not driver_revenue.empty else None

# Optional: format top driver name
top_driver_name = None
if top_driver_id:
    driver_row = drivers[drivers["driver_id"] == top_driver_id]
    if not driver_row.empty:
        top_driver_name = f"{driver_row.iloc[0]['first_name']} {driver_row.iloc[0]['last_name']}"

# -------------------------------
# KPI DISPLAY
# -------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Drivers", total_drivers)
col2.metric("Total Active Drivers", active_drivers)
col3.metric("Total Terminated Drivers", terminated_drivers)
col4.metric("Total Revenue", f"${total_revenue/1_000_000:.2f}M")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Top Driver by Revenue", top_driver_name if top_driver_name else "N/A")
col2.metric("Trips Completed", f"{total_trips:,.0f}")
col3.metric("Total Miles Driven", f"{total_miles/1_000_000:.2f}M")
col4.metric("Profit Margin", "59.38%")  # Optional: calculate if needed

# -------------------------------
# ANALYSIS: Employment Status
# -------------------------------
employment_pct = drivers["employment_status"].value_counts(normalize=True) * 100
fig1, ax1 = plt.subplots(figsize=(5,5))
ax1.pie(
    employment_pct,
    labels=employment_pct.index,
    autopct="%1.1f%%",
    startangle=90
)
ax1.set_title("Driver Employment Status (%)")
st.pyplot(fig1)

# -------------------------------
# ANALYSIS: Experience Buckets
# -------------------------------
drivers["exp_bucket"] = pd.cut(
    drivers["years_experience"],
    bins=[0, 2, 5, 10, 30],
    labels=["0–2 Years", "3–5 Years", "6–10 Years", "10+ Years"]
)

exp_pct = drivers["exp_bucket"].value_counts(normalize=True).sort_index() * 100
fig2, ax2 = plt.subplots(figsize=(8,5))
bars = ax2.bar(exp_pct.index.astype(str), exp_pct.values)
ax2.set_xlabel("Experience Level")
ax2.set_ylabel("Percentage of Drivers")
ax2.set_title("Driver Experience Buckets (% of Total Drivers)")

# Add % labels above bars
for bar in bars:
    ax2.text(
        bar.get_x() + bar.get_width()/2,
        bar.get_height(),
        f"{bar.get_height():.1f}%",
        ha="center",
        va="bottom"
    )
ax2.set_ylim(0, exp_pct.max() + 5)
st.pyplot(fig2)

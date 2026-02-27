import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_loader import load_all_tables
from src.filters import apply_global_filters


# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------
st.title(":green[Route & Trip Efficiency 🗺️]")


# --------------------------------------------------
# LOAD + FILTER DATA
# --------------------------------------------------
data = load_all_tables()
data = apply_global_filters(data)

trips = data["trips"]
loads = data["loads"]
fuel = data["fuel_purchases"]
routes = data["routes"]


# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

total_trips = trips["trip_id"].nunique()
total_miles = trips["actual_distance_miles"].sum()

total_revenue = loads["revenue"].sum()
total_fuel_cost = fuel["total_cost"].sum()

# Revenue per mile
revenue_per_mile = (
    total_revenue / total_miles if total_miles > 0 else 0
)

# Profit & Margin
total_profit = total_revenue - total_fuel_cost
profit_margin = (
    (total_profit / total_revenue) * 100
    if total_revenue > 0 else 0
)

# Average Load Weight
avg_weight = loads["weight_lbs"].mean()

# Idle Time per Trip
if "idle_hours" in trips.columns:
    idle_time_per_trip = trips["idle_hours"].mean()
else:
    idle_time_per_trip = 0

# Avg Trip Duration per Route
if "trip_duration_hours" in trips.columns:
    avg_trip_duration = trips["trip_duration_hours"].mean()
else:
    avg_trip_duration = 0

# Average MPG (Miles / Gallons)
total_gallons = fuel["gallons"].sum()
avg_mpg = (
    total_miles / total_gallons if total_gallons > 0 else 0
)


# --------------------------------------------------
# KPI DISPLAY
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)
col1.metric("Average MPG", f"{avg_mpg:.2f}")
col2.metric("Revenue per Mile", f"${revenue_per_mile:.2f}")
col3.metric("Idle Time per Trip", f"{idle_time_per_trip:.2f} hrs")
col4.metric("Trips Completed", f"{total_trips:,}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Average Load Weight", f"{avg_weight:,.0f}")
col2.metric("Avg Trip Duration", f"{avg_trip_duration:.2f} hrs")
col3.metric("Total Profit", f"${total_profit/1_000_000:.2f}M")
col4.metric("Profit Margin", f"{profit_margin:.2f}%")


# ==================================================
# OPTIONAL ANALYSIS (Route-Level Efficiency)
# ==================================================

if "route_id" in trips.columns:

    route_perf = (
        trips.groupby("route_id")["distance_miles"]
        .sum()
        .reset_index()
        .sort_values("distance_miles", ascending=False)
        .head(10)
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(
        data=route_perf,
        x="route_id",
        y="distance_miles",
        ax=ax
    )

    ax.set_title("Top 10 Routes by Distance Covered")
    ax.set_xlabel("Route")
    ax.set_ylabel("Total Miles")
    plt.xticks(rotation=45)

    st.pyplot(fig)

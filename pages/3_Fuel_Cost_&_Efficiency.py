import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
 
from src.data_loader import load_all_tables
from src.filters import apply_global_filters
 
 
# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------
st.title(":green[Fuel Cost & Efficiency ⛽]")
 
 
# --------------------------------------------------
# LOAD + FILTER DATA
# --------------------------------------------------
data = load_all_tables()
data = apply_global_filters(data)
 
fuel = data["fuel_purchases"]
trips = data["trips"]
trucks = data["trucks"]
 
 
# --------------------------------------------------
# KPI CALCULATIONS (Dynamic)
# --------------------------------------------------
 
fuel["purchase_date"] = pd.to_datetime(fuel["purchase_date"], errors="coerce")
 
total_spend = fuel["total_cost"].sum()
total_gallons = fuel["gallons"].sum()
avg_price = total_spend / total_gallons if total_gallons > 0 else 0
 
total_miles = trips["actual_distance_miles"].sum()
fuel_cost_per_mile = total_spend / total_miles if total_miles > 0 else 0
 
fuel_per_trip = total_spend / trips["trip_id"].nunique()
fuel_per_truck = total_spend / trucks["truck_id"].nunique()
 
avg_mpg = total_miles / total_gallons if total_gallons > 0 else 0
 
idle_pct = (
    trips["idle_hours"].sum() /
    trips["total_hours"].sum() * 100
    if "idle_hours" in trips.columns and "total_hours" in trips.columns
    else 0
)
 
 
# --------------------------------------------------
# KPI DISPLAY
# --------------------------------------------------
 
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Fuel Spend", f"${total_spend/1_000_000:.2f}M")
col2.metric("Total Gallons Purchased", f"{total_gallons/1_000_000:.2f}M")
col3.metric("Average Price per Gallon", f"${avg_price:.2f}")
col4.metric("Fuel Cost per Mile", f"${fuel_cost_per_mile:.2f}")
 
col1, col2, col3, col4 = st.columns(4)
col1.metric("Fuel Cost per Trip", f"${fuel_per_trip:,.0f}")
col2.metric("Average Fuel per Truck", f"${fuel_per_truck/1_000:.2f}K")
col3.metric("Average MPG", f"{avg_mpg:.2f}")
col4.metric("Idle Hours %", f"{idle_pct:.2f}%")
 
 
# ==================================================
# MONTHLY FUEL COST TREND
# ==================================================
 
fuel["month"] = fuel["purchase_date"].dt.month
 
monthly_fuel = (
    fuel.groupby("month")["total_cost"]
    .sum()
    .reset_index()
    .sort_values("month")
)
 
fig, ax = plt.subplots(figsize=(8, 4))
 
sns.lineplot(
    data=monthly_fuel,
    x="month",
    y="total_cost",
    marker="o",
    color="green",
    ax=ax
)
 
ax.set_title("Total Fuel Cost by Month")
ax.set_xlabel("Month")
ax.set_ylabel("Total Fuel Cost ($)")
 
ax.set_xticks(range(1, 13))
ax.set_xticklabels(
    ["Jan","Feb","Mar","Apr","May","Jun",
     "Jul","Aug","Sep","Oct","Nov","Dec"]
)
 
for _, row in monthly_fuel.iterrows():
    ax.text(
        row["month"],
        row["total_cost"],
        f"{row['total_cost']/1_000_000:.2f}M",
        ha="center"
    )
 
st.pyplot(fig)

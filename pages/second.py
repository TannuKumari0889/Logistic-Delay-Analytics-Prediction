import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_loader import load_all_tables
from src.filters import apply_global_filters

# --------------------------------------------------
# PAGE CONFIG & PROFESSIONAL STYLING
# --------------------------------------------------
st.set_page_config(layout="wide", page_title="Executive Fleet Insights")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #2e7d32;
    }
    </style>
    """, unsafe_allow_html=True)

st.title(":green[Fleet & Fuel Executive Master Dashboard 🚛⛽]")
st.markdown("---")

# --------------------------------------------------
# LOAD + FILTER DATA
# --------------------------------------------------
data = load_all_tables()
data = apply_global_filters(data)

trucks = data["trucks"]
trips = data["trips"]
trailers = data["trailers"]
fuel = data["fuel_purchases"]
truck_util = data["truck_utilization_metrics"]
maintenance = data["maintenance_records"]

# --------------------------------------------------
# MASTER CALCULATIONS (Error-Protected)
# --------------------------------------------------
fuel["purchase_date"] = pd.to_datetime(fuel["purchase_date"], errors="coerce")

# Fleet Calcs
total_trucks = trucks["truck_id"].nunique()
active_trucks = trucks[trucks["status"] == "Active"]["truck_id"].nunique()
total_trips = trips["trip_id"].nunique()
total_miles = trips["actual_distance_miles"].sum()
avg_util = truck_util["utilization_rate"].mean()
total_downtime = maintenance["downtime_hours"].sum()
maintenance_count = maintenance["maintenance_id"].nunique()

# Fuel Calcs
total_spend = fuel["total_cost"].sum()
total_gallons = fuel["gallons"].sum()
avg_price = total_spend / total_gallons if total_gallons > 0 else 0
fuel_cost_per_mile = total_spend / total_miles if total_miles > 0 else 0
fuel_per_trip = total_spend / total_trips if total_trips > 0 else 0
fuel_per_truck = total_spend / total_trucks if total_trucks > 0 else 0
avg_mpg = total_miles / total_gallons if total_gallons > 0 else 0

# Safety Check for Idle Hours
if "idle_hours" in trips.columns and "total_hours" in trips.columns:
    idle_pct = (trips["idle_hours"].sum() / trips["total_hours"].sum()) * 100
else:
    idle_pct = 0.0

# --------------------------------------------------
# KPI SECTION: 16 METRICS (4 Rows of 4)
# --------------------------------------------------
st.subheader("🌐 Fleet Operational Excellence")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Avg Utilization Rate", f"{avg_util:.2%}")
c2.metric("Total Miles Driven", f"{total_miles:,.0f}")
c3.metric("Total Trips", f"{total_trips:,}")
c4.metric("Total Trucks", total_trucks)

c5, c6, c7, c8 = st.columns(4)
c5.metric("Active Trucks", active_trucks)
c6.metric("Total Downtime Hours", f"{total_downtime:,.0f}")
c7.metric("Maintenance Events", maintenance_count)
c8.metric("Avg Trips per Truck", f"{total_trips/total_trucks:.2f}")

st.markdown("---")
st.subheader("⛽ Fuel Economy & Efficiency")
c9, c10, c11, c12 = st.columns(4)
c9.metric("Total Fuel Spend", f"${total_spend/1_000_000:.2f}M")
c10.metric("Total Gallons", f"{total_gallons/1_000_000:.2f}M")
c11.metric("Avg Price / Gal", f"${avg_price:.2f}")
c12.metric("Fuel Cost / Mile", f"${fuel_cost_per_mile:.2f}")

c13, c14, c15, c16 = st.columns(4)
c13.metric("Fuel Cost / Trip", f"${fuel_per_trip:,.0f}")
c14.metric("Avg Fuel / Truck", f"${fuel_per_truck/1_000:.2f}K")
c15.metric("Average MPG", f"{avg_mpg:.2f}")
c16.metric("Idle Hours %", f"{idle_pct:.1f}%")

st.markdown("---")

# --------------------------------------------------
# VISUALIZATION GRID (5 Charts)
# --------------------------------------------------
sns.set_theme(style="whitegrid")
col_left, col_right = st.columns(2)

with col_left:
    # 1. Monthly Trend
    st.write("#### 📈 Monthly Fuel Cost Trend")
    fuel["month"] = fuel["purchase_date"].dt.month
    m_fuel = fuel.groupby("month")["total_cost"].sum().reset_index()
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    sns.lineplot(data=m_fuel, x="month", y="total_cost", marker="o", color="green", ax=ax1)
    plt.xticks(range(1, 13), ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
    st.pyplot(fig1)

    # 2. Utilization Pie
    st.write("#### 🎯 Fleet Utilization Distribution")
    truck_util["category"] = truck_util["utilization_rate"].apply(lambda x: "Underutilized" if x < 0.7 else ("Optimal" if x <= 1 else "Overutilized"))
    util_dist = truck_util["category"].value_counts(normalize=True) * 100
    fig2, ax2 = plt.subplots(figsize=(5, 5))
    ax2.pie(util_dist, labels=util_dist.index, autopct="%1.1f%%", colors=["#ff9999","#66b3ff","#99ff99"])
    st.pyplot(fig2)

with col_right:
    # 3. Fuel Cost by Trailer Type
    st.write("#### 📦 Fuel Cost by Trailer Type")
    f_merge = fuel.merge(trips, on="trip_id").merge(trailers, on="trailer_id")
    f_type = f_merge.groupby("trailer_type")["total_cost"].sum().reset_index().sort_values("total_cost", ascending=False)
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    sns.barplot(data=f_type, x="trailer_type", y="total_cost", palette="viridis", ax=ax3)
    plt.xticks(rotation=45)
    st.pyplot(fig3)

    # 4. Trailer Age Distribution
    st.write("#### ⏳ Trip Distribution by Trailer Age")
    trailers["age"] = 2025 - trailers["model_year"]
    trailers["age_group"] = pd.cut(trailers["age"], bins=[0, 3, 7, 10], labels=["0-3 Yrs", "4-7 Yrs", "8-10 Yrs"])
    age_merge = trips.merge(trailers[["trailer_id", "age_group"]], on="trailer_id", how="inner")
    age_dist = age_merge.groupby("age_group")["trip_id"].count().reset_index()
    fig4, ax4 = plt.subplots(figsize=(8, 4))
    sns.barplot(data=age_dist, x="age_group", y="trip_id", palette="magma", ax=ax4)
    st.pyplot(fig4)

# 5. Full Width Truck Status
st.markdown("---")
st.write("#### 🚛 Fleet Status Distribution (%)")
status_dist = trucks["status"].value_counts(normalize=True) * 100
fig5, ax5 = plt.subplots(figsize=(14, 3))
sns.barplot(x=status_dist.index, y=status_dist.values, palette="coolwarm", ax=ax5)
for i, val in enumerate(status_dist.values):
    ax5.text(i, val + 1, f"{val:.1f}%", ha="center")
st.pyplot(fig5)

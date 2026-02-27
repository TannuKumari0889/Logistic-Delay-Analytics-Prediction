import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_loader import load_all_tables
from src.filters import apply_global_filters

# --------------------------------------------------
# PAGE CONFIG & THEMING
# --------------------------------------------------
st.set_page_config(layout="wide", page_title="Fleet Executive Insights")

# Custom CSS for a professional "Card" look
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #2e7d32;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True) # FIXED THIS LINE

st.title("📊 Fleet & Fuel Executive Insights")
st.markdown("---")

# --------------------------------------------------
# DATA ENGINE
# --------------------------------------------------
data = load_all_tables()
data = apply_global_filters(data)

trucks, trips, trailers = data["trucks"], data["trips"], data["trailers"]
fuel, truck_util, maintenance = data["fuel_purchases"], data["truck_utilization_metrics"], data["maintenance_records"]

# Logic for all 16 KPIs
fuel["purchase_date"] = pd.to_datetime(fuel["purchase_date"], errors="coerce")
total_trucks, total_trips = trucks["truck_id"].nunique(), trips["trip_id"].nunique()
total_miles, total_spend = trips["actual_distance_miles"].sum(), fuel["total_cost"].sum()
total_gallons = fuel["gallons"].sum()

# --------------------------------------------------
# SECTION 1: FLEET PERFORMANCE (8 KPIs)
# --------------------------------------------------
with st.container():
    st.subheader("🌐 Fleet Operations Overview")
    
    # Row 1
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Utilization", f"{truck_util['utilization_rate'].mean():.2%}")
    col2.metric("Total Miles", f"{total_miles:,.0f}")
    col3.metric("Total Trips", f"{total_trips:,}")
    col4.metric("Fleet Size", total_trucks)

    # Row 2
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Active Trucks", trucks[trucks["status"] == "Active"]["truck_id"].nunique())
    col6.metric("Downtime (Hrs)", f"{maintenance['downtime_hours'].sum():,.0f}")
    col7.metric("Maint. Events", maintenance["maintenance_id"].nunique())
    col8.metric("Trips / Truck", f"{(total_trips / total_trucks):.2f}")

st.markdown("---")

# --------------------------------------------------
# SECTION 2: FUEL & EFFICIENCY (8 KPIs)
# --------------------------------------------------
with st.container():
    st.subheader("⛽ Fuel Economy & Financials")
    
    # Row 3
    col9, col10, col11, col12 = st.columns(4)
    col9.metric("Total Fuel Spend", f"${total_spend/1_000_000:.2f}M", delta_color="inverse")
    col10.metric("Gallons Consumed", f"{total_gallons/1_000_000:.2f}M")
    col11.metric("Avg Price/Gal", f"${(total_spend / total_gallons):.2f}")
    col12.metric("Fuel Cost/Mile", f"${(total_spend / total_miles):.2f}")

    # Row 4
    col13, col14, col15, col16 = st.columns(4)
    col13.metric("Cost per Trip", f"${(total_spend / total_trips):,.0f}")
    col14.metric("Avg Fuel/Truck", f"${(total_spend / total_trucks / 1000):.1f}K")
    col15.metric("Avg MPG", f"{(total_miles / total_gallons):.2f}")
    col16.metric("Idle Hours %", f"{(trips['idle_hours'].sum()/trips['total_hours'].sum()*100):.1f}%")

st.markdown("---")

# --------------------------------------------------
# SECTION 3: ANALYTICS VISUALS
# --------------------------------------------------
# Apply a clean seaborn theme
sns.set_theme(style="whitegrid", palette="muted")

chart_col1, chart_col2 = st.columns([1.2, 1], gap="large")

with chart_col1:
    # 1. Trend Analysis
    st.markdown("#### 📈 Fuel Spend Seasonality")
    fuel["month"] = fuel["purchase_date"].dt.month
    monthly_data = fuel.groupby("month")["total_cost"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=monthly_data, x="month", y="total_cost", marker="o", color="#2e7d32", linewidth=2.5)
    plt.xticks(range(1, 13), ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    st.pyplot(fig)

    # 2. Status Distribution
    st.markdown("#### 🚛 Fleet Status Health")
    status_data = trucks["status"].value_counts(normalize=True) * 100
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    sns.barplot(x=status_data.index, y=status_data.values, palette="Greens_d")
    st.pyplot(fig2)

with chart_col2:
    # 3. Utilization Pie
    st.markdown("#### 🎯 Capacity Utilization")
    truck_util["cat"] = pd.cut(truck_util["utilization_rate"], bins=[0, 0.7, 1.0, 5], labels=["Under", "Optimal", "Over"])
    util_pie = truck_util["cat"].value_counts()
    fig3, ax3 = plt.subplots()
    ax3.pie(util_pie, labels=util_pie.index, autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99'], startangle=140)
    st.pyplot(fig3)

    # 4. Trailer Costs
    st.markdown("#### 📦 Fuel Cost by Trailer")
    f_merge = fuel.merge(trips, on="trip_id").merge(trailers, on="trailer_id")
    trailer_cost = f_merge.groupby("trailer_type")["total_cost"].sum().sort_values(ascending=False)
    fig4, ax4 = plt.subplots()
    trailer_cost.plot(kind="barh", color="#1b5e20", ax=ax4)
    st.pyplot(fig4)

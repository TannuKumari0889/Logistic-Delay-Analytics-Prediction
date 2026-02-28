import streamlit as st

# If the user hasn't logged in on the main page, stop them here
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("Please log in on the Home page to access this dashboard.")
    st.stop()


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_loader import load_all_tables
from src.filters import apply_global_filters

# --------------------------------------------------
# PAGE CONFIG & PROFESSIONAL STYLING
# --------------------------------------------------
st.set_page_config(layout="wide", page_title="Fleet & Fuel Analytics")

# Custom CSS for "Card" styling and professional metrics
st.markdown("""
    <style>
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 6px solid #2e7d32;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

st.title(":green[Fleet & Fuel Analytics 🚛⛽]")
st.markdown("---")

# --------------------------------------------------
# DATA ENGINE
# --------------------------------------------------
data = load_all_tables()
data = apply_global_filters(data)

trucks, trips, trailers = data["trucks"], data["trips"], data["trailers"]
fuel, truck_util, maintenance = data["fuel_purchases"], data["truck_utilization_metrics"], data["maintenance_records"]

# --------------------------------------------------
# UNIT MANAGEMENT HELPER
# --------------------------------------------------
def format_metric(value, prefix=""):
    if value >= 1_000_000:
        return f"{prefix}{value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{prefix}{value/1_000:.1f}K"
    else:
        return f"{prefix}{value:,.2f}"

# --------------------------------------------------
# MASTER KPI CALCULATIONS
# --------------------------------------------------
fuel["purchase_date"] = pd.to_datetime(fuel["purchase_date"], errors="coerce")
total_spend = fuel["total_cost"].sum()
total_miles = trips["actual_distance_miles"].sum()
total_gallons = fuel["gallons"].sum()
total_trips = trips["trip_id"].nunique()
total_trucks = trucks["truck_id"].nunique()

# Safety Check for Idle Hours
if "idle_hours" in trips.columns and "total_hours" in trips.columns:
    idle_pct = (trips["idle_hours"].sum() / trips["total_hours"].sum()) * 100
else:
    idle_pct = 0.0

# --------------------------------------------------
# KPI SECTION: 16 METRICS
# --------------------------------------------------
st.subheader("🌐 Fleet Operational Excellence")
r1_1, r1_2, r1_3, r1_4 = st.columns(4)
r1_1.metric("Avg Utilization", f"{truck_util['utilization_rate'].mean():.1%}")
r1_2.metric("Total Distance", format_metric(total_miles))
r1_3.metric("Total Trips", f"{total_trips:,}")
r1_4.metric("Total Fleet", total_trucks)

r2_1, r2_2, r2_3 = st.columns(3)
r2_1.metric("Active Units", trucks[trucks["status"] == "Active"]["truck_id"].nunique())
r2_2.metric("Downtime (Hrs)", format_metric(maintenance["downtime_hours"].sum()))
r2_3.metric("Maint. Events", maintenance["maintenance_id"].nunique())


st.markdown("---")
st.subheader("⛽ Fuel Financials & Efficiency")
r3_1, r3_2, r3_3, r3_4 = st.columns(4)
r3_1.metric("Total Fuel Cost", format_metric(total_spend, "$"))
r3_2.metric("Total Fuel (Gal)", format_metric(total_gallons))
r3_3.metric("Avg Price/Gal", f"${(total_spend/total_gallons):.2f}")
r3_4.metric("Fuel Cost / Mile", f"${(total_spend/total_miles):.2f}")



st.markdown("---")

# --------------------------------------------------
# VISUALIZATION GRID (4 Major Charts)
# --------------------------------------------------
sns.set_theme(style="white")
c_left, c_right = st.columns(2)

with c_left:
    # 1. Monthly Trend (Line Chart with % Labels)
    st.write("#### 📈 Monthly Fuel Spend Distribution")
    fuel["month"] = fuel["purchase_date"].dt.month
    monthly_data = fuel.groupby("month")["total_cost"].sum().reset_index()
    monthly_data["pct"] = (monthly_data["total_cost"] / total_spend) * 100
    
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    sns.lineplot(data=monthly_data, x="month", y="pct", marker="o", color="#1b5e20", linewidth=3, ax=ax1)
    for i, row in monthly_data.iterrows():
        ax1.text(row['month'], row['pct'] + 0.3, f"{row['pct']:.1f}%", ha='center', fontweight='bold', color='#1b5e20')
    plt.xticks(range(1, 13), ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    ax1.set_ylabel("Share of Annual Cost (%)")
    st.pyplot(fig1)

    # 2. Fuel Cost by Trailer (Pie Chart)
    st.write("#### 🥧 Fuel Cost by Trailer Type")
    f_merge = fuel.merge(trips, on="trip_id").merge(trailers, on="trailer_id")
    trailer_pie = f_merge.groupby("trailer_type")["total_cost"].sum()
    fig2, ax2 = plt.subplots()
    ax2.pie(trailer_pie, labels=trailer_pie.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("viridis"))
    st.pyplot(fig2)

with c_right:
    # 3. Trip Distribution by Trailer Age (Bar with % Labels)
    st.write("#### ⏳ Trip Distribution by Trailer Age")
    trailers["age"] = 2025 - trailers["model_year"]
    trailers["age_grp"] = pd.cut(trailers["age"], bins=[0, 3, 7, 10], labels=["0-3 Yrs", "4-7 Yrs", "8-10 Yrs"])
    age_merge = trips.merge(trailers[["trailer_id", "age_grp"]], on="trailer_id")
    age_dist = age_merge.groupby("age_grp")["trip_id"].count().reset_index()
    age_dist["pct"] = (age_dist["trip_id"] / age_dist["trip_id"].sum()) * 100
    
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    sns.barplot(data=age_dist, x="age_grp", y="pct", palette="Greens_d", ax=ax3)
    for i, val in enumerate(age_dist["pct"]):
        ax3.text(i, val + 1, f"{val:.1f}%", ha='center', fontweight='bold')
    ax3.set_ylabel("Share of Total Trips (%)")
    st.pyplot(fig3)

    # 4. Utilization Pie
    st.write("#### 🎯 Fleet Utilization Distribution")
    truck_util["cat"] = pd.cut(truck_util["utilization_rate"], bins=[0, 0.7, 1.0, 5], labels=["Under", "Optimal", "Over"])
    util_pie = truck_util["cat"].value_counts()
    fig4, ax4 = plt.subplots()
    ax4.pie(util_pie, labels=util_pie.index, autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99'], startangle=140)
    st.pyplot(fig4)

# 5. Full Width Status Bar (Professional Finish)
st.markdown("---")
st.write("#### 🚛 Current Fleet Health Status (%)")
status_data = trucks["status"].value_counts(normalize=True) * 100
fig5, ax5 = plt.subplots(figsize=(15, 3))
sns.barplot(x=status_data.index, y=status_data.values, palette="YlGn_r", ax=ax5)
for i, val in enumerate(status_data.values):
    ax5.text(i, val + 2, f"{val:.1f}%", ha="center", fontweight="bold")
ax5.set_ylim(0, 110)
st.pyplot(fig5)

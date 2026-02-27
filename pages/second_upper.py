import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_loader import load_all_tables
from src.filters import apply_global_filters

# --------------------------------------------------
# PAGE CONFIG & PROFESSIONAL STYLING
# --------------------------------------------------
st.set_page_config(layout="wide", page_title="Master Fleet & Maintenance Hub")

st.markdown("""
    <style>
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #2e7d32;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# DATA ENGINE
# --------------------------------------------------
data = load_all_tables()
data = apply_global_filters(data)

trucks, trips, trailers = data["trucks"], data["trips"], data["trailers"]
fuel, truck_util, maintenance = data["fuel_purchases"], data["truck_utilization_metrics"], data["maintenance_records"]

def format_metric(value, prefix=""):
    if value >= 1_000_000:
        return f"{prefix}{value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{prefix}{value/1_000:.1f}K"
    else:
        return f"{prefix}{value:,.2f}"

# --------------------------------------------------
# MASTER CALCULATIONS
# --------------------------------------------------
fuel["purchase_date"] = pd.to_datetime(fuel["purchase_date"], errors="coerce")
total_spend = fuel["total_cost"].sum()
total_miles = trips["actual_distance_miles"].sum()
total_gallons = fuel["gallons"].sum()
total_trips = trips["trip_id"].nunique()
total_trucks = trucks["truck_id"].nunique()
total_maint_cost = maintenance["total_cost"].sum()

if "idle_hours" in trips.columns and "total_hours" in trips.columns:
    idle_pct = (trips["idle_hours"].sum() / trips["total_hours"].sum()) * 100
else:
    idle_pct = 0.0

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title(":green[Fleet, Fuel & Maintenance Control 🚛🛠️]")

# --------------------------------------------------
# SECTION 1: ALL 16 FLEET & FUEL KPIs
# --------------------------------------------------
st.subheader("🌐 Fleet Operational Excellence")
r1_1, r1_2, r1_3, r1_4 = st.columns(4)
r1_1.metric("Avg Utilization", f"{truck_util['utilization_rate'].mean():.1%}")
r1_2.metric("Total Distance", format_metric(total_miles))
r1_3.metric("Total Trips", f"{total_trips:,}")
r1_4.metric("Total Fleet", total_trucks)

r2_1, r2_2, r2_3, r2_4 = st.columns(4)
r2_1.metric("Active Units", trucks[trucks["status"] == "Active"]["truck_id"].nunique())
r2_2.metric("Downtime (Hrs)", format_metric(maintenance["downtime_hours"].sum()))
r2_3.metric("Maint. Events", maintenance["maintenance_id"].nunique())
r2_4.metric("Trips per Truck", f"{(total_trips/total_trucks):.2f}")

st.subheader("⛽ Fuel Financials & Efficiency")
r3_1, r3_2, r3_3, r3_4 = st.columns(4)
r3_1.metric("Total Fuel Cost", format_metric(total_spend, "$"))
r3_2.metric("Total Fuel (Gal)", format_metric(total_gallons))
r3_3.metric("Avg Price/Gal", f"${(total_spend/total_gallons):.2f}")
r3_4.metric("Fuel Cost / Mile", f"${(total_spend/total_miles):.2f}")

r4_1, r4_2, r4_3, r4_4 = st.columns(4)
r4_1.metric("Avg Cost / Trip", format_metric(total_spend/total_trips, "$"))
r4_2.metric("Avg Cost / Truck", format_metric(total_spend/total_trucks, "$"))
r4_3.metric("Fleet Avg MPG", f"{(total_miles/total_gallons):.2f}")
r4_4.metric("Idle Time %", f"{idle_pct:.1f}%")

st.markdown("---")

# --------------------------------------------------
# SECTION 2: INTEGRATED CHARTS (Both Dashboards)
# --------------------------------------------------
st.subheader("📊 Analytics Insight Gallery")
sns.set_theme(style="white")

col_a, col_b = st.columns(2)

with col_a:
    # Chart 1: Monthly Fuel (From Code 1)
    st.write("#### 📈 Monthly Fuel Spend Distribution")
    fuel["month"] = fuel["purchase_date"].dt.month
    monthly_data = fuel.groupby("month")["total_cost"].sum().reset_index()
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    sns.lineplot(data=monthly_data, x="month", y="total_cost", marker="o", color="#1b5e20", ax=ax1)
    st.pyplot(fig1)

    # Chart 2: Maintenance Distribution (From Code 2)
    st.write("#### 🔧 Maintenance Type Distribution (%)")
    maint_dist = maintenance["maintenance_type"].value_counts(normalize=True) * 100
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.barplot(x=maint_dist.index, y=maint_dist.values, palette="viridis", ax=ax2)
    st.pyplot(fig2)

with col_b:
    # Chart 3: Trailer Age (From Code 1)
    st.write("#### ⏳ Trip Distribution by Trailer Age")
    trailers["age"] = 2026 - trailers["model_year"]
    trailers["age_grp"] = pd.cut(trailers["age"], bins=[0, 3, 7, 10], labels=["0-3 Yrs", "4-7 Yrs", "8-10 Yrs"])
    age_merge = trips.merge(trailers[["trailer_id", "age_grp"]], on="trailer_id")
    age_dist = age_merge.groupby("age_grp")["trip_id"].count().reset_index()
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    sns.barplot(data=age_dist, x="age_grp", y="trip_id", palette="Greens_d", ax=ax3)
    st.pyplot(fig3)

    # Chart 4: Fuel Cost Pie (From Code 1)
    st.write("#### 🥧 Fuel Cost by Trailer Type")
    f_merge = fuel.merge(trips, on="trip_id").merge(trailers, on="trailer_id")
    trailer_pie = f_merge.groupby("trailer_type")["total_cost"].sum()
    fig4, ax4 = plt.subplots()
    ax4.pie(trailer_pie, labels=trailer_pie.index, autopct='%1.1f%%', startangle=140)
    st.pyplot(fig4)

# Full Width Status Bar (Professional Finish)
st.markdown("---")
st.write("#### 🚛 Current Fleet Health Status (%)")
status_data = trucks["status"].value_counts(normalize=True) * 100
fig5, ax5 = plt.subplots(figsize=(15, 3))
sns.barplot(x=status_data.index, y=status_data.values, palette="YlGn_r", ax=ax5)
st.pyplot(fig5)

import streamlit as st
'''
# If the user hasn't logged in on the main page, stop them here
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("Please log in on the Home page to access this dashboard.")
    st.stop()
'''

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_loader import load_all_tables
from src.filters import apply_global_filters

# --------------------------------------------------
# PAGE CONFIG & PROFESSIONAL WHITE THEME
# --------------------------------------------------
st.set_page_config(layout="wide", page_title="Driver Performance")

# Restore original professional styling
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

st.title(":green[Driver Performance 👨‍✈️]")
st.markdown("---")

# --------------------------------------------------
# DATA ENGINE
# --------------------------------------------------
data = load_all_tables()
data = apply_global_filters(data)

drivers = data["drivers"]
driver_metrics = data["driver_monthly_metrics"]
loads = data["loads"]

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------
total_drivers = len(drivers)
active_drivers = len(drivers[drivers["employment_status"] == "Active"])
terminated_drivers = len(drivers[drivers["employment_status"] == "Terminated"])
total_revenue = loads["revenue"].sum()
total_trips = driver_metrics["trips_completed"].sum()
total_miles = driver_metrics["total_miles"].sum()

driver_revenue = driver_metrics.groupby("driver_id")["total_revenue"].sum()
top_driver_id = driver_revenue.idxmax() if not driver_revenue.empty else None

top_driver_name = "N/A"
if top_driver_id:
    driver_row = drivers[drivers["driver_id"] == top_driver_id]
    if not driver_row.empty:
        top_driver_name = f"{driver_row.iloc[0]['first_name']} {driver_row.iloc[0]['last_name']}"

# --------------------------------------------------
# KPI DISPLAY (8 Metrics)
# --------------------------------------------------
r1_1, r1_2, r1_3, r1_4 = st.columns(4)
r1_1.metric("Total Drivers", total_drivers)
r1_2.metric("Active Drivers", active_drivers)
r1_3.metric("Terminated", terminated_drivers)
r1_4.metric("Total Revenue", f"${total_revenue/1_000_000:.2f}M")

r2_1, r2_2, r2_3= st.columns(3)
r2_1.metric("Top Driver", top_driver_name)
r2_2.metric("Trips Completed", f"{total_trips:,.0f}")
r2_3.metric("Total Miles Driven", f"{total_miles/1_000_000:.2f}M")


st.markdown("---")

# --------------------------------------------------
# VISUALIZATION (Professional Styling)
# --------------------------------------------------
sns.set_theme(style="white")
c_left, c_right = st.columns(2)

with c_left:
    st.write("#### 🥧 Driver Employment Status (%)")
    employment_pct = drivers["employment_status"].value_counts(normalize=True) * 100
    fig1, ax1 = plt.subplots(figsize=(5, 5))
    ax1.pie(
        employment_pct, 
        labels=employment_pct.index, 
        autopct="%1.1f%%", 
        startangle=90, 
        colors=sns.color_palette("Greens_r")
    )
    st.pyplot(fig1)

with c_right:
    st.write("#### 📊 Driver Experience Buckets")
    drivers["exp_bucket"] = pd.cut(
        drivers["years_experience"],
        bins=[0, 2, 5, 10, 30],
        labels=["0–2 Years", "3–5 Years", "6–10 Years", "10+ Years"]
    )
    exp_pct = drivers["exp_bucket"].value_counts(normalize=True).sort_index() * 100
    
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.barplot(x=exp_pct.index.astype(str), y=exp_pct.values, palette="Greens_d", ax=ax2)
    
    # Add labels above bars
    for i, val in enumerate(exp_pct.values):
        ax2.text(i, val + 1, f"{val:.1f}%", ha="center", fontweight='bold')
    
    ax2.set_ylabel("Percentage (%)")
    ax2.set_ylim(0, exp_pct.max() + 10)
    st.pyplot(fig2)

st.markdown("---")
st.caption("Driver Performance Module | GitHub Analytics Dashboard")

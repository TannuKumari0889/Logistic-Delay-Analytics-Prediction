import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_loader import load_all_tables
from src.filters import apply_global_filters

# -------------------------------
# 🌙 DARK THEME & STYLING
# -------------------------------
st.set_page_config(layout="wide", page_title="Driver Performance")

st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    /* Metric Card Styling */
    [data-testid="stMetric"] {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    }
    [data-testid="stMetricLabel"] {
        color: #8b949e !important;
    }
    h1, h2, h3 {
        color: #4cd964 !important; /* Brighter green for headers */
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Driver Performance 👨‍✈️")
st.markdown("---")

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

total_revenue = driver_metrics["total_revenue"].sum()
total_trips = driver_metrics["trips_completed"].sum()
total_miles = driver_metrics["total_miles"].sum()

driver_revenue = driver_metrics.groupby("driver_id")["total_revenue"].sum()
top_driver_id = driver_revenue.idxmax() if not driver_revenue.empty else None

top_driver_name = "N/A"
if top_driver_id:
    driver_row = drivers[drivers["driver_id"] == top_driver_id]
    if not driver_row.empty:
        top_driver_name = f"{driver_row.iloc[0]['first_name']} {driver_row.iloc[0]['last_name']}"

# -------------------------------
# KPI DISPLAY (Row 1)
# -------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Drivers", total_drivers)
c2.metric("Total Active", active_drivers)
c3.metric("Total Terminated", terminated_drivers)
c4.metric("Total Revenue", f"${total_revenue/1_000_000:.2f}M")

# KPI DISPLAY (Row 2)
c5, c6, c7, c8 = st.columns(4)
c5.metric("Top Driver", top_driver_name)
c6.metric("Trips Completed", f"{total_trips:,.0f}")
c7.metric("Total Miles", f"{total_miles/1_000_000:.2f}M")
c8.metric("Profit Margin", "59.38%")

st.markdown("---")

# -------------------------------
# ANALYSIS: DARK CHARTS
# -------------------------------
plt.style.use("dark_background") # Force Matplotlib into dark mode

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Employment Status")
    employment_pct = drivers["employment_status"].value_counts(normalize=True) * 100
    fig1, ax1 = plt.subplots(figsize=(6, 5), facecolor='#161b22')
    ax1.set_facecolor('#161b22')
    
    # Using a modern color palette
    colors = ['#4cd964', '#ff3b30', '#ff9500'] 
    ax1.pie(
        employment_pct, 
        labels=employment_pct.index, 
        autopct="%1.1f%%", 
        startangle=90, 
        colors=colors,
        wedgeprops={'edgecolor': '#161b22', 'linewidth': 2}
    )
    st.pyplot(fig1)

with col_right:
    st.subheader("Experience Level Distribution")
    drivers["exp_bucket"] = pd.cut(
        drivers["years_experience"],
        bins=[0, 2, 5, 10, 30],
        labels=["0–2 Yrs", "3–5 Yrs", "6–10 Yrs", "10+ Yrs"]
    )
    exp_pct = drivers["exp_bucket"].value_counts(normalize=True).sort_index() * 100
    
    fig2, ax2 = plt.subplots(figsize=(8, 5), facecolor='#161b22')
    ax2.set_facecolor('#161b22')
    
    bars = ax2.bar(exp_pct.index.astype(str), exp_pct.values, color='#007aff')
    
    # Clean up axes for dark mode
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.set_ylabel("Percentage (%)", color='#8b949e')

    for bar in bars:
        ax2.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height(),
            f"{bar.get_height():.1f}%",
            ha="center", va="bottom", color="white", fontweight='bold'
        )
    st.pyplot(fig2)

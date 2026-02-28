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
# PAGE CONFIG & PROFESSIONAL THEME (Green/White)
# --------------------------------------------------
st.set_page_config(layout="wide", page_title="Safety & Risk")

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

st.title(":green[Safety & Risk Performance 🚨]")
st.markdown("---")

# -------------------------------
# LOAD + FILTER DATA
# -------------------------------
data = load_all_tables()
data = apply_global_filters(data)

incidents = data["safety_incidents"]
trips = data["trips"] 

# -------------------------------
# KPI CALCULATIONS
# -------------------------------
total_incidents = len(incidents)

preventable_pct = ((incidents["preventable_flag"] == 1).sum() / total_incidents * 100 if total_incidents > 0 else 0)
at_fault_pct = ((incidents["at_fault_flag"] == 1).sum() / total_incidents * 100 if total_incidents > 0 else 0)
injury_pct = ((incidents["injury_flag"] == 1).sum() / total_incidents * 100 if total_incidents > 0 else 0)

total_cost = incidents[["vehicle_damage_cost","cargo_damage_cost","claim_amount"]].sum().sum()
avg_cost = total_cost / total_incidents if total_incidents > 0 else 0

total_miles = trips["actual_distance_miles"].sum()
incident_rate_per_100k = (total_incidents / total_miles * 100_000 if total_miles > 0 else 0)
incident_cost_per_mile = (total_cost / total_miles if total_miles > 0 else 0)

# -------------------------------
# KPI DISPLAY (8 Metrics)
# -------------------------------
st.subheader("⚠️ Incident Overview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Incidents", total_incidents)
col2.metric("Preventable %", f"{preventable_pct:.2f}%")
col3.metric("At-Fault Rate %", f"{at_fault_pct:.2f}%")
col4.metric("Injury Rate %", f"{injury_pct:.2f}%")

st.markdown("<br>", unsafe_allow_html=True) # Spacer

col5, col6, col7, col8 = st.columns(4)
col5.metric("Avg Cost / Incident", f"${avg_cost:,.2f}")
col6.metric("Total Incident Cost", f"${total_cost/1_000_000:.2f}M")
col7.metric("Rate / 100k Miles", f"{incident_rate_per_100k:.2f}")
col8.metric("Cost per Mile", f"${incident_cost_per_mile:.4f}")

st.markdown("---")

# -------------------------------
# VISUAL ANALYSIS (Professional Layout)
# -------------------------------
sns.set_theme(style="white")
c1, c2, c3 = st.columns(3)

# Common styling for the pie charts
pie_colors = sns.color_palette("Greens_r", 2)
risk_colors = ["#e1e4e8", "#d32f2f"] # Gray for "Safe", Red for "Risk"

with c1:
    st.write("#### 🏥 Injury Involvement")
    injury_pct_data = incidents["injury_flag"].value_counts(normalize=True) * 100
    fig1, ax1 = plt.subplots(figsize=(5,5))
    ax1.pie(injury_pct_data, labels=["No Injury","Injury"], autopct="%1.1f%%", 
            startangle=90, colors=risk_colors, wedgeprops={'edgecolor': 'white'})
    st.pyplot(fig1)

with c2:
    st.write("#### ⚖️ At-Fault Share")
    at_fault_data = incidents["at_fault_flag"].value_counts(normalize=True).sort_index() * 100
    fig2, ax2 = plt.subplots(figsize=(5,5))
    ax2.pie(at_fault_data, labels=["Not At Fault","At Fault"], autopct="%1.1f%%", 
            startangle=90, colors=risk_colors, wedgeprops={'edgecolor': 'white'})
    st.pyplot(fig2)

with c3:
    st.write("#### 🛡️ Preventability")
    preventable_data = incidents["preventable_flag"].value_counts(normalize=True) * 100
    fig3, ax3 = plt.subplots(figsize=(5,5))
    ax3.pie(preventable_data, labels=["Non-Preventable","Preventable"], autopct="%1.1f%%", 
            startangle=90, colors=risk_colors, wedgeprops={'edgecolor': 'white'})
    st.pyplot(fig3)

st.markdown("---")
st.caption("Safety & Risk Dashboard | Fleet Management System")

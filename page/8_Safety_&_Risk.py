import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src.data_loader import load_all_tables
from src.filters import apply_global_filters

# -------------------------------
# PAGE TITLE
# -------------------------------
st.title(":green[Safety & Risk 🚨]")

# -------------------------------
# LOAD + FILTER DATA
# -------------------------------
data = load_all_tables()
data = apply_global_filters(data)

incidents = data["safety_incidents"]
trips = data["trips"]  # for distance-based KPIs

# -------------------------------
# KPI CALCULATIONS
# -------------------------------

total_incidents = len(incidents)

preventable_pct = (
    (incidents["preventable_flag"] == 1).sum() / total_incidents * 100
    if total_incidents > 0 else 0
)

at_fault_pct = (
    (incidents["at_fault_flag"] == 1).sum() / total_incidents * 100
    if total_incidents > 0 else 0
)

injury_pct = (
    (incidents["injury_flag"] == 1).sum() / total_incidents * 100
    if total_incidents > 0 else 0
)

# Total cost = sum of all relevant cost columns
total_cost = incidents[["vehicle_damage_cost","cargo_damage_cost","claim_amount"]].sum().sum()
avg_cost = total_cost / total_incidents if total_incidents > 0 else 0

# Incident rate per 100k miles
total_miles = trips["actual_distance_miles"].sum()
incident_rate_per_100k = (
    total_incidents / total_miles * 100_000
    if total_miles > 0 else 0
)

# Incident cost per mile
incident_cost_per_mile = (
    total_cost / total_miles if total_miles > 0 else 0
)

# -------------------------------
# KPI DISPLAY
# -------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Incidents", total_incidents)
col2.metric("Preventable Incident %", f"{preventable_pct:.2f}%")
col3.metric("At-Fault Rate %", f"{at_fault_pct:.2f}%")
col4.metric("Injury Rate %", f"{injury_pct:.2f}%")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Average Cost per Incident", f"${avg_cost:,.2f}")
col2.metric("Total Incident Cost", f"${total_cost/1_000_000:.2f}M")
col3.metric("Incident Rate per 100k Miles", f"{incident_rate_per_100k:.2f}")
col4.metric("Incident Cost per Mile", f"${incident_cost_per_mile:.4f}")

# -------------------------------
# PIE CHART ANALYSIS
# -------------------------------

# 1️⃣ Injury Involvement
injury_pct_data = incidents["injury_flag"].value_counts(normalize=True) * 100
fig1, ax1 = plt.subplots(figsize=(4,4))
ax1.pie(
    injury_pct_data,
    labels=["No Injury","Injury"],
    autopct="%1.1f%%",
    startangle=90
)
ax1.set_title("Injury Involvement (%)")
st.pyplot(fig1)

# 2️⃣ At-Fault Share
at_fault_data = incidents["at_fault_flag"].value_counts(normalize=True).sort_index() * 100
fig2, ax2 = plt.subplots(figsize=(5,5))
ax2.pie(
    at_fault_data,
    labels=["Not At Fault","At Fault"],
    autopct="%1.1f%%",
    startangle=90
)
ax2.set_title("At-Fault Incident Share (%)")
st.pyplot(fig2)

# 3️⃣ Preventable Incidents
preventable_data = incidents["preventable_flag"].value_counts(normalize=True) * 100
fig3, ax3 = plt.subplots(figsize=(5,5))
ax3.pie(
    preventable_data,
    labels=["Non-Preventable","Preventable"],
    autopct="%1.1f%%",
    startangle=90
)
ax3.set_title("Incident Preventability (%)")
st.pyplot(fig3)

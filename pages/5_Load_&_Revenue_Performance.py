import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_loader import load_all_tables
from src.filters import apply_global_filters


# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------
st.title(":green[Load & Revenue Performance 💰]")


# --------------------------------------------------
# LOAD + FILTER DATA
# --------------------------------------------------
data = load_all_tables()
data = apply_global_filters(data)

loads = data["loads"]
customers = data["customers"]
fuel = data["fuel_purchases"]


# --------------------------------------------------
# KPI CALCULATIONS (Dynamic)
# --------------------------------------------------

total_revenue = loads["revenue"].sum()
total_loads = loads["load_id"].nunique()

avg_revenue_per_load = (
    total_revenue / total_loads if total_loads > 0 else 0
)

avg_weight = loads["weight_lbs"].mean()

fuel_surcharge = loads["fuel_surcharge"].sum() \
    if "fuel_surcharge" in loads.columns else 0

accessorial_charge = loads["accessorial_charge"].sum() \
    if "accessorial_charge" in loads.columns else 0

# On-Time %
if "delivery_status" in loads.columns:
    on_time_pct = (
        (loads["delivery_status"] == "On Time").sum() /
        total_loads * 100
        if total_loads > 0 else 0
    )
else:
    on_time_pct = 0

# Profit Margin (Revenue - Fuel Cost) / Revenue
total_fuel_cost = fuel["total_cost"].sum()
profit_margin = (
    ((total_revenue - total_fuel_cost) / total_revenue) * 100
    if total_revenue > 0 else 0
)


# --------------------------------------------------
# KPI DISPLAY
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${total_revenue/1_000_000:.2f}M")
col2.metric("Avg Revenue per Load", f"${avg_revenue_per_load:,.0f}")
col3.metric("Total Loads Completed", f"{total_loads:,}")
col4.metric("On-Time Delivery %", f"{on_time_pct:.2f}%")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Average Load Weight", f"{avg_weight:,.0f}")
col2.metric("Total Fuel Surcharge", f"${fuel_surcharge/1_000_000:.2f}M")
col3.metric("Total Accessorial Charge", f"${accessorial_charge/1_000_000:.2f}M")
col4.metric("Profit Margin", f"{profit_margin:.2f}%")


# ==================================================
# 1️⃣ Revenue Share by Booking Type
# ==================================================

booking_rev = (
    loads.groupby("booking_type")["revenue"]
    .sum()
)

booking_pct = booking_rev / booking_rev.sum() * 100

fig1, ax1 = plt.subplots(figsize=(5, 5))
ax1.pie(
    booking_pct,
    labels=booking_pct.index,
    autopct="%1.1f%%"
)
ax1.set_title("Revenue Share by Booking Type (%)")

st.pyplot(fig1)


# ==================================================
# 2️⃣ Revenue Distribution by Customer Status
# ==================================================

load_customer = loads.merge(
    customers[["customer_id", "account_status"]],
    on="customer_id",
    how="left"
)

rev_status = (
    load_customer.groupby("account_status")["revenue"]
    .sum()
)

fig2, ax2 = plt.subplots(figsize=(5, 5))
ax2.pie(
    rev_status,
    labels=rev_status.index,
    autopct="%1.1f%%",
    startangle=90
)
ax2.set_title("Revenue Distribution by Customer Status")

st.pyplot(fig2)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_loader import load_all_tables
from src.filters import apply_global_filters

# --------------------------------------------------
# PAGE CONFIG & PREMIUM THEME
# --------------------------------------------------
st.set_page_config(layout="wide", page_title="Executive Overview")

# Deep Green & Slate Gray Professional Theme
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .stMetric {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-top: 5px solid #1b5e20;
    }
    h1, h2, h3 { color: #1b5e20; font-family: 'Helvetica Neue', sans-serif; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Executive Overview")
st.markdown("---")

# --------------------------------------------------
# DATA ENGINE
# --------------------------------------------------
data = load_all_tables()
data = apply_global_filters(data)

# Extract Tables
customers = data["customers"]
loads = data["loads"]
delivery_events = data["delivery_events"]
facilities = data["facilities"]
trips = data["trips"]
fuel_purchases = data["fuel_purchases"]
maintenance_records = data["maintenance_records"]
safety_incidents = data["safety_incidents"]

# --------------------------------------------------
# UNIT FORMATTING HELPER
# --------------------------------------------------
def format_val(value, is_money=True):
    prefix = "$" if is_money else ""
    if value >= 1_000_000:
        return f"{prefix}{value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{prefix}{value/1_000:.1f}K"
    return f"{prefix}{value:,.0f}"

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------
total_revenue = loads["revenue"].sum()
total_fuel = fuel_purchases["total_cost"].sum()
total_maint = maintenance_records["total_cost"].sum()
total_safe = safety_incidents["cost"].sum() if "cost" in safety_incidents.columns else 0

total_profit = total_revenue - (total_fuel + total_maint + total_safe)
profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

# --------------------------------------------------
# KPI DISPLAY (2 Rows)
# --------------------------------------------------
with st.container():
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers", f"{customers['customer_id'].nunique():,}")
    c2.metric("Total Loads", f"{loads['load_id'].count()/1000:,.1f}K")
    c3.metric("Total Revenue", format_val(total_revenue))
    c4.metric("Fuel Expenses", format_val(total_fuel))
    
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Maintenance", format_val(total_maint))
    c6.metric("Incident Costs", format_val(total_safe))
    c7.metric("Net Profit", format_val(total_profit))
    c8.metric("Profit Margin", f"{profit_margin:.1f}%")

st.markdown("---")

# --------------------------------------------------
# VISUAL ANALYTICS (2x2 Grid)
# --------------------------------------------------
sns.set_theme(style="white")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # 1. Customer Distribution (Pie)
    if "account_status" in customers.columns:
        st.subheader("Customer Distribution")
        c_status = customers["account_status"].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(c_status, labels=c_status.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Greens"))
        st.pyplot(fig1)

    # 2. Revenue Share by Booking Type (Pie)
    if "booking_type" in loads.columns:
        st.subheader("Revenue by Booking Type")
        data_bt = loads.groupby("booking_type")["revenue"].sum()
        fig2, ax2 = plt.subplots()
        ax2.pie(data_bt, labels=data_bt.index, autopct='%1.1f%%', colors=sns.color_palette("viridis"))
        st.pyplot(fig2)

with chart_col2:
    # 3. Revenue by Customer Status (Pie)
    if "customer_id" in loads.columns:
        st.subheader("Revenue by Customer Status")
        load_cust = loads.merge(customers, on="customer_id", how="left")
        rev_status = load_cust.groupby("account_status")["revenue"].sum()
        fig3, ax3 = plt.subplots()
        ax3.pie(rev_status, labels=rev_status.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("YlGnBu"))
        st.pyplot(fig3)

    # 4. Facility Usage (Pie)
    if "facility_id" in delivery_events.columns:
        st.subheader("Facility Usage (%)")
        fac_events = delivery_events.merge(facilities, on="facility_id", how="left")
        fac_usage = fac_events["facility_type"].value_counts()
        fig4, ax4 = plt.subplots()
        ax4.pie(fac_usage, labels=fac_usage.index, autopct='%1.1f%%', colors=sns.color_palette("mako"))
        st.pyplot(fig4)

st.markdown("---")

# --------------------------------------------------
# TRENDS SECTION (Full Width)
# --------------------------------------------------
t_col1, t_col2 = st.columns([2, 1])

with t_col1:
    st.subheader("Revenue Seasonality Trend")
    if "load_date" in loads.columns:
        loads["load_date"] = pd.to_datetime(loads["load_date"], errors="coerce")
        loads["Year"] = loads["load_date"].dt.year
        loads["Month"] = loads["load_date"].dt.month
        monthly_rev = loads.groupby(["Year", "Month"])["revenue"].sum().reset_index()
        
        fig5, ax5 = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=monthly_rev, x="Month", y="revenue", hue="Year", marker="o", palette="dark:green", ax=ax5)
        plt.xticks(range(1,13), ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
        st.pyplot(fig5)

with t_col2:
    st.subheader("Trips Growth by Year")
    if "dispatch_date" in trips.columns:
        trips["dispatch_date"] = pd.to_datetime(trips["dispatch_date"], errors="coerce")
        trips["Year"] = trips["dispatch_date"].dt.year
        y_trips = trips.groupby("Year")["trip_id"].count().reset_index()
        
        fig6, ax6 = plt.subplots(figsize=(5, 6))
        sns.barplot(data=y_trips, x="Year", y="trip_id", palette="Greens_d", ax=ax6)
        # Add Percentage Labels
        total_y_trips = y_trips["trip_id"].sum()
        for i, val in enumerate(y_trips["trip_id"]):
            pct = (val / total_y_trips) * 100
            ax6.text(i, val, f"{pct:.1f}%", ha='center', va='bottom', fontweight='bold')
        st.pyplot(fig6)

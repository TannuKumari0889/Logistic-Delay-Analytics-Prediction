import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns # Added for better styling
 
from src.data_loader import load_all_tables
from src.filters import apply_global_filters
 
# --------------------------------------------------
# PAGE CONFIG & THEME
# --------------------------------------------------
st.set_page_config(layout="wide", page_title="Executive Dashboard")
sns.set_theme(style="whitegrid") # Sets a clean background for all plots
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=sns.color_palette("viridis", 10)) 

st.title("📊 Executive Overview")
st.markdown("---")
 
# ================= LOAD DATA =================
data = load_all_tables()
data = apply_global_filters(data)
 
customers = data["customers"]
loads = data["loads"]
delivery_events = data["delivery_events"]
facilities = data["facilities"]
trips = data["trips"]
fuel_purchases = data["fuel_purchases"]
maintenance_records = data["maintenance_records"]
safety_incidents = data["safety_incidents"]
 
# ================= CALCULATIONS =================
total_revenue = loads["revenue"].sum() / 1_000_000
total_fuel_cost = fuel_purchases["total_cost"].sum()
total_maintenance = maintenance_records["total_cost"].sum()
total_incident_cost = safety_incidents["cost"].sum() if "cost" in safety_incidents.columns else 0
 
total_profit = (total_revenue * 1_000_000) - (total_fuel_cost + total_maintenance + total_incident_cost)
profit_margin = (total_profit / (total_revenue * 1_000_000) * 100) if total_revenue > 0 else 0
 
# ================= KPI SECTION (Professional Grid) =================
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", f"{customers['customer_id'].nunique():,}")
    col2.metric("Total Loads", f"{loads['load_id'].count()/1000:,.1f}K")
    col3.metric("Total Revenue", f"${total_revenue:,.2f}M")
    col4.metric("Fuel Expenses", f"${total_fuel_cost/1_000_000:,.2f}M")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Maintenance", f"${total_maintenance/1_000:,.1f}K")
    col2.metric("Incident Costs", f"${total_incident_cost/1_000:,.1f}K")
    col3.metric("Total Profit", f"${total_profit/1_000_000:,.2f}M")
    col4.metric("Profit Margin", f"{profit_margin:.1f}%")

st.markdown("---")
 
# ================= CHARTS SECTION (Side-by-Side) =================
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # CUSTOMER STATUS
    if "account_status" in customers.columns:
        st.subheader("Customer Health")
        customer_status_count = customers["account_status"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(customer_status_count, labels=customer_status_count.index, autopct="%1.1f%%", startangle=140, colors=sns.color_palette("pastel"))
        st.pyplot(fig)

    # CUSTOMER TYPE
    if "customer_type" in customers.columns:
        st.subheader("Booking Type Mix")
        data_ct = customers["customer_type"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(data_ct, labels=data_ct.index, autopct="%1.1f%%", colors=sns.color_palette("magma"))
        st.pyplot(fig)

with chart_col2:
    # REVENUE BY STATUS
    if "customer_id" in loads.columns:
        st.subheader("Revenue by Status")
        load_customer = loads.merge(customers, on="customer_id", how="left")
        revenue_by_status = load_customer.groupby("account_status")["revenue"].sum()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(revenue_by_status, labels=revenue_by_status.index, autopct="%1.1f%%", startangle=140, colors=sns.color_palette("viridis"))
        st.pyplot(fig)

    # FACILITY USAGE
    if "facility_id" in delivery_events.columns:
        st.subheader("Facility Usage (%)")
        events_facilities = delivery_events.merge(facilities, on="facility_id", how="left")
        data_fac = events_facilities["facility_type"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(data_fac, labels=data_fac.index, autopct="%1.1f%%", colors=sns.color_palette("rocket"))
        st.pyplot(fig)

st.markdown("---")

# ================= TRENDS SECTION (Full Width) =================
trend_col1, trend_col2 = st.columns([2, 1])

with trend_col1:
    st.subheader("Revenue Seasonality Trend")
    if "load_date" in loads.columns:
        loads["load_date"] = pd.to_datetime(loads["load_date"], errors="coerce")
        loads["Year"] = loads["load_date"].dt.year
        loads["Month"] = loads["load_date"].dt.month
        monthly_revenue = loads.groupby(["Year", "Month"])["revenue"].sum().reset_index().sort_values(["Year", "Month"])

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=monthly_revenue, x="Month", y="revenue", hue="Year", marker="o", palette="viridis")
        plt.xticks(range(1,13), ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
        st.pyplot(fig)

with trend_col2:
    st.subheader("Trips by Year")
    if "dispatch_date" in trips.columns:
        trips["dispatch_date"] = pd.to_datetime(trips["dispatch_date"], errors="coerce")
        trips["Year"] = trips["dispatch_date"].dt.year
        trips_by_year = trips.groupby("Year")["trip_id"].count().reset_index()
        
        fig, ax = plt.subplots(figsize=(5, 7.5))
        sns.barplot(data=trips_by_year, x="Year", y="trip_id", palette="Blues_d")
        st.pyplot(fig)

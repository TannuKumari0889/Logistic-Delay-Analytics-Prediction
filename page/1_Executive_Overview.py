import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
 
from src.data_loader import load_all_tables
from src.filters import apply_global_filters
 
st.title("Executive Overview 🚀")
 
# ================= LOAD DATA =================
data = load_all_tables()
 
# Apply global slicers
data = apply_global_filters(data)
 
customers = data["customers"]
loads = data["loads"]
delivery_events = data["delivery_events"]
facilities = data["facilities"]
trips = data["trips"]
fuel_purchases = data["fuel_purchases"]
maintenance_records = data["maintenance_records"]
safety_incidents = data["safety_incidents"]
 
# ================= KPIs =================
 
total_revenue = loads["revenue"].sum()/1000000
total_fuel_cost = fuel_purchases["total_cost"].sum()
total_maintenance = maintenance_records["total_cost"].sum()
total_incident_cost = safety_incidents["cost"].sum() if "cost" in safety_incidents.columns else 0
 
total_profit = total_revenue - (
    total_fuel_cost + total_maintenance + total_incident_cost
)
 
profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
 
col1, col2, col3, col4 = st.columns(4)
col1.metric("Customers", customers["customer_id"].nunique())
col2.metric("Loads", loads["load_id"].count()/1000,"K")
col3.metric("Revenue", f"${total_revenue:,.2f}M")
col4.metric("Fuel Cost", f"${total_fuel_cost:,.0f}")
 
col1, col2, col3, col4 = st.columns(4)
col1.metric("Maintenance Cost", f"${total_maintenance:,.0f}")
col2.metric("Incident Cost", f"${total_incident_cost:,.0f}")
col3.metric("Total Profit", f"${total_profit:,.0f}")
col4.metric("Profit Margin", f"{profit_margin:.2f}%")
 
st.divider()
 
# ================= CUSTOMER STATUS =================
if "account_status" in customers.columns:
    customer_status_count = customers["account_status"].value_counts()
 
    fig = plt.figure(figsize=(4,4))
    plt.pie(customer_status_count,
            labels=customer_status_count.index,
            autopct="%1.1f%%",
            startangle=90)
    plt.title("Customer Distribution by Status")
    st.pyplot(fig)
 
# ================= REVENUE BY CUSTOMER STATUS =================
if "customer_id" in loads.columns:
    load_customer = loads.merge(customers, on="customer_id", how="left")
    revenue_by_status = load_customer.groupby("account_status")["revenue"].sum()
 
    fig = plt.figure(figsize=(5,5))
    plt.pie(revenue_by_status,
            labels=revenue_by_status.index,
            autopct="%1.1f%%",
            startangle=90)
    plt.title("Revenue Distribution by Customer Status")
    st.pyplot(fig)
 
# ================= CUSTOMER TYPE =================
if "customer_type" in customers.columns:
    data_ct = customers["customer_type"].value_counts(normalize=True) * 100
 
    fig = plt.figure(figsize=(5,5))
    plt.pie(data_ct, labels=data_ct.index, autopct="%1.1f%%")
    plt.title("Customers by Booking Type (%)")
    st.pyplot(fig)
 
# ================= REVENUE BY BOOKING TYPE =================
if "booking_type" in loads.columns:
    data_bt = loads.groupby("booking_type")["revenue"].sum()
    data_bt = (data_bt / data_bt.sum()) * 100
 
    fig = plt.figure(figsize=(5,5))
    plt.pie(data_bt, labels=data_bt.index, autopct="%1.1f%%")
    plt.title("Revenue Share by Booking Type (%)")
    st.pyplot(fig)
 
# ================= FACILITY USAGE =================
if "facility_id" in delivery_events.columns:
    events_facilities = delivery_events.merge(
        facilities,
        on="facility_id",
        how="left"
    )
 
    data_fac = events_facilities["facility_type"].value_counts(normalize=True) * 100
 
    fig = plt.figure(figsize=(5,5))
    plt.pie(data_fac, labels=data_fac.index, autopct="%1.1f%%")
    plt.title("Facility Type Usage During Events (%)")
    st.pyplot(fig)
 
# ================= REVENUE SEASONALITY =================
if "load_date" in loads.columns:
    loads["load_date"] = pd.to_datetime(loads["load_date"], errors="coerce")
    loads["Year"] = loads["load_date"].dt.year
    loads["Month"] = loads["load_date"].dt.month
 
    monthly_revenue = (
        loads.groupby(["Year", "Month"])["revenue"]
        .sum()
        .reset_index()
        .sort_values(["Year", "Month"])
    )
 
    fig = plt.figure(figsize=(7,4))
 
    for year in monthly_revenue["Year"].dropna().unique():
        d = monthly_revenue[monthly_revenue["Year"] == year]
        plt.plot(d["Month"], d["revenue"], marker="o", label=str(int(year)))
 
    plt.xticks(range(1,13),
               ['Jan','Feb','Mar','Apr','May','Jun',
                'Jul','Aug','Sep','Oct','Nov','Dec'])
 
    plt.xlabel("Month")
    plt.ylabel("Total Revenue")
    plt.title("Revenue Seasonality Trend by Year")
    plt.legend()
    plt.grid(True)
    st.pyplot(fig)
 
# ================= TRIPS BY YEAR =================
if "dispatch_date" in trips.columns:
    trips["dispatch_date"] = pd.to_datetime(trips["dispatch_date"], errors="coerce")
    trips["Year"] = trips["dispatch_date"].dt.year
 
    trips_by_year = trips.groupby("Year")["trip_id"].count().reset_index()
 
    total_trips = trips_by_year["trip_id"].sum()
    trips_by_year["Percentage"] = (
        trips_by_year["trip_id"] / total_trips * 100
    )
 
    fig = plt.figure(figsize=(7,5))
    bars = plt.bar(trips_by_year["Year"], trips_by_year["trip_id"])
 
    for bar, pct in zip(bars, trips_by_year["Percentage"]):
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width()/2,
            height,
            f"{pct:.1f}%",
            ha="center",
            va="bottom"
        )
 
    plt.xlabel("Year")
    plt.ylabel("Total Trips")
    plt.title("Total Trips by Year (%)")
    plt.xticks(trips_by_year["Year"])
    st.pyplot(fig)

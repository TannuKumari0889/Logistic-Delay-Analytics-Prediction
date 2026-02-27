# src/filters.py
import streamlit as st
import pandas as pd
 
def apply_global_filters(data_dict):
    """
    Applies global filters to the entire dataset.
    New filters:
    - Month & Year (loads)
    - Booking Type (loads)
    - Model Year (trucks)
    - Maintenance Type (maintenance_records)
    - Customer Type (customers)
    """
    st.sidebar.header("🔎 Global Filters")
 
    # ---------------------------
    # Tables to work with
    # ---------------------------
    customers = data_dict["customers"]
    drivers = data_dict["drivers"]
    loads = data_dict["loads"]
    trips = data_dict["trips"]
    fuel_purchases = data_dict["fuel_purchases"]
    maintenance_records = data_dict["maintenance_records"]
    safety_incidents = data_dict["safety_incidents"]
    trucks = data_dict["trucks"]
    truck_metrics = data_dict.get("truck_utilization_metrics", pd.DataFrame())
 
    # ---------------------------
    # DATE FILTER (Month & Year from loads)
    # ---------------------------
    if "load_date" in loads.columns:
        loads["load_date"] = pd.to_datetime(loads["load_date"], errors="coerce")
        loads["month"] = loads["load_date"].dt.month
        loads["year"] = loads["load_date"].dt.year
 
        # Year filter
        years = sorted(loads["year"].dropna().unique())
        selected_years = st.sidebar.multiselect("Select Year", options=years, default=years)
        loads = loads[loads["year"].isin(selected_years)]
 
        # Month filter
        months = sorted(loads["month"].dropna().unique())
        selected_months = st.sidebar.multiselect("Select Month", options=months, default=months)
        loads = loads[loads["month"].isin(selected_months)]
 
        trips = trips[trips["load_id"].isin(loads["load_id"])]
 
    # ---------------------------
    # BOOKING TYPE FILTER
    # ---------------------------
    if "booking_type" in loads.columns:
        booking_options = loads["booking_type"].dropna().unique()
        selected_booking = st.sidebar.multiselect(
            "Select Booking Type", options=booking_options, default=booking_options
        )
        loads = loads[loads["booking_type"].isin(selected_booking)]
        trips = trips[trips["load_id"].isin(loads["load_id"])]
 
    # ---------------------------
    # CUSTOMER TYPE FILTER
    # ---------------------------
    if "customer_type" in customers.columns:
        customer_options = customers["customer_type"].dropna().unique()
        selected_customer_type = st.sidebar.multiselect(
            "Select Customer Type", options=customer_options, default=customer_options
        )
        customers = customers[customers["customer_type"].isin(selected_customer_type)]
        loads = loads[loads["customer_id"].isin(customers["customer_id"])]
        trips = trips[trips["load_id"].isin(loads["load_id"])]
 
    # ---------------------------
    # MODEL YEAR FILTER (trucks)
    # ---------------------------
    if "model_year" in trucks.columns:
        years_options = sorted(trucks["model_year"].dropna().unique())
        selected_model_year = st.sidebar.multiselect(
            "Select Truck Model Year", options=years_options, default=years_options
        )
        trucks = trucks[trucks["model_year"].isin(selected_model_year)]
        trips = trips[trips["truck_id"].isin(trucks["truck_id"])]
 
    # ---------------------------
    # MAINTENANCE TYPE FILTER
    # ---------------------------
    if "maintenance_type" in maintenance_records.columns:
        maint_options = maintenance_records["maintenance_type"].dropna().unique()
        selected_maint_type = st.sidebar.multiselect(
            "Select Maintenance Type", options=maint_options, default=maint_options
        )
        maintenance_records = maintenance_records[
            maintenance_records["maintenance_type"].isin(selected_maint_type)
        ]
        # Optional: filter trucks in maintenance
        trucks_in_maint = maintenance_records["truck_id"].dropna().unique()
        trips = trips[trips["truck_id"].isin(trucks_in_maint)]
 
    # ---------------------------
    # Update dependent tables
    # ---------------------------
    fuel_purchases = fuel_purchases[fuel_purchases["trip_id"].isin(trips["trip_id"])]
    safety_incidents = safety_incidents[safety_incidents["trip_id"].isin(trips["trip_id"])]
    maintenance_records = maintenance_records[
        maintenance_records["truck_id"].isin(trips["truck_id"].dropna().unique())
    ]
    if not truck_metrics.empty:
        truck_metrics = truck_metrics[
            truck_metrics["truck_id"].isin(trips["truck_id"].dropna().unique())
        ]
 
    # ---------------------------
    # Update dictionary
    # ---------------------------
    data_dict["customers"] = customers
    data_dict["loads"] = loads
    data_dict["trips"] = trips
    data_dict["drivers"] = drivers
    data_dict["fuel_purchases"] = fuel_purchases
    data_dict["maintenance_records"] = maintenance_records
    data_dict["safety_incidents"] = safety_incidents
    data_dict["trucks"] = trucks
    data_dict["truck_utilization_metrics"] = truck_metrics
 
    return data_dict

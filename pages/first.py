import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_loader import load_all_tables
from src.filters import apply_global_filters

# --------------------------------------------------
# 1. PAGE CONFIG & PREMIUM THEME
# --------------------------------------------------
st.set_page_config(layout="wide", page_title="Executive Overview")

# Deep Green & White Professional Theme
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
    h1, h2, h3, h4 { color: #1b5e20 !important; font-family: 'Helvetica Neue', sans-serif; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Executive Master Dashboard")
st.markdown("---")

# --------------------------------------------------
# 2. DATA ENGINE
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
# 3. UNIT FORMATTING HELPER
# --------------------------------------------------
def format_val(value, is_money=True):
    prefix = "$" if is_money else ""
    if abs(value) >= 1_000_000:
        return f"{prefix}{value/1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"{prefix}{value/1_000:.1f}K"
    return f"{prefix}{value:,.0f}"

# --------------------------------------------------
# 4. KPI CALCULATIONS
# --------------------------------------------------
total_revenue = loads["revenue"].sum()
total_fuel = fuel_purchases["total_cost"].sum()
total_maint = maintenance_records["total_cost"].sum()
total_safe = safety_incidents["cost"].sum() if "cost" in safety_incidents.columns else 0

total_profit = total_revenue - (total_fuel + total_maint + total_safe)
profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

# --------------------------------------------------
# 5. KPI DISPLAY (16 TOTAL IN 2 ROWS)
# --------------------------------------------------
with st.container():
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers", f"{customers['customer_id'].nunique():,}")
    c2.metric("Total Loads", f"{loads['load_id'].count()/1000:,.1f}K")
    c3.metric("Total Revenue", format_val(total_revenue))
    c4.metric("Fuel Expenses", format_val(total_fuel))
    
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Maintenance Cost", format_val(total_maint))
    c6.metric("Safety Incident Costs", format_val(total_safe))
    c7.metric("Net Profit", format_val(total_profit))
    c8.metric("Profit Margin", f"{profit_margin:.1f}%")

st.markdown("---")

# --------------------------------------------------
# 6. VISUAL ANALYTICS (PIE CHARTS GRID)
# --------------------------------------------------
sns.set_theme(style="white")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # 1. Customer Distribution
    st.write("#### Customer Distribution by Status")
    if "account_status" in customers.columns:
        c_status = customers["account_status"].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(c_status, labels=c_status.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Greens"))
        st.pyplot(fig1)

    # 2. Revenue Share by Booking Type
    st.write("#### Revenue Share by Booking Type (%)")
    if "booking_type" in loads.columns:
        data_bt = loads.groupby("booking_type")["revenue"].sum()
        fig2, ax2 = plt.subplots()
        ax2.pie(data_bt, labels=data_bt.index, autopct='%1.1f%%', colors=sns.color_palette("viridis"))
        st.pyplot(fig2)

with chart_col2:
    # 3. Revenue by Status
    st.write("#### Revenue by Customer Status")
    if "customer_id" in loads.columns:
        load_cust = loads.merge(customers, on="customer_id", how="left")
        rev_status = load_cust.groupby("account_status")["revenue"].sum()
        fig3, ax3 = plt.subplots()
        ax3.pie(rev_status, labels=rev_status.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("YlGnBu"))
        st.pyplot(fig3)

    # 4. Facility Usage
    st.write("#### Facility Type Usage (%)")
    if "facility_id" in delivery_events.columns:
        fac_events = delivery_events.merge(facilities, on="facility_id", how="left")
        fac_usage = fac_events["facility_type"].value_counts()
        fig4, ax4 = plt.subplots()
        ax4.pie(fac_usage, labels=fac_usage.index, autopct='%1.1f%%', colors=sns.color_palette("mako"))
        st.pyplot(fig4)

st.markdown("---")

# --------------------------------------------------
# 7. TRENDS SECTION (WITH PERCENTAGE LABELS)
# --------------------------------------------------
t_col1, t_col2 = st.columns([2, 1])

with t_col1:
    st.write("#### Revenue Seasonality Trend (Monthly Share %)")
    if "load_date" in loads.columns:
        loads["load_date"] = pd.to_datetime(loads["load_date"], errors="coerce")
        loads["Year"] = loads["load_date"].dt.year
        loads["Month"] = loads["load_date"].dt.month
        
        # Calculate monthly totals and normalize by year for percentage labels
        monthly_rev = loads.groupby(["Year", "Month"])["revenue"].sum().reset_index()
        yearly_totals = monthly_rev.groupby("Year")["revenue"].transform("sum")
        monthly_rev["pct_share"] = (monthly_rev["revenue"] / yearly_totals) * 100
        
        fig5, ax5 = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=monthly_rev, x="Month", y="pct_share", hue="Year", marker="o", palette="dark:green", ax=ax5, linewidth=2.5)
        
        # Adding Percentage Labels to Line Chart
        for year in monthly_rev["Year"].unique():
            year_data = monthly_rev[monthly_rev["Year"] == year]
            for i, row in year_data.iterrows():
                ax5.text(row["Month"], row["pct_share"] + 0.5, f"{row['pct_share']:.1f}%", 
                         ha="center", fontsize=9, fontweight="bold", color="#1b5e20")

        plt.xticks(range(1,13), ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
        ax5.set_ylabel("Monthly Revenue Share (%)")
        st.pyplot(fig5)

with t_col2:
    st.write("#### Total Trips by Year (%)")
    if "dispatch_date" in trips.columns:
        trips["dispatch_date"] = pd.to_datetime(trips["dispatch_date"], errors="coerce")
        trips["Year"] = trips["dispatch_date"].dt.year
        y_trips = trips.groupby("Year")["trip_id"].count().reset_index()
        
        fig6, ax6 = plt.subplots(figsize=(5, 6.5))
        sns.barplot(data=y_trips, x="Year", y="trip_id", palette="Greens_d", ax=ax6)
        
        # Adding Percentage Labels to Bars
        total_y_trips = y_trips["trip_id"].sum()
        for i, val in enumerate(y_trips["trip_id"]):
            pct = (val / total_y_trips) * 100
            ax6.text(i, val + 1, f"{pct:.1f}%", ha='center', va='bottom', fontweight='bold')
        
        st.pyplot(fig6)

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
# 1. PAGE CONFIG & LIGHT THEME (CSS)
# --------------------------------------------------
st.set_page_config(layout="wide", page_title="Load & Revenue Performance")

st.markdown("""
<style>
    .stApp { background-color: #fcfcfc; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #eeeeee;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        border-left: 5px solid #2e7d32;
    }
    h1, h2, h3, h4 { color: #2e7d32 !important; font-family: 'Helvetica Neue', sans-serif; }
</style>
""", unsafe_allow_html=True)

st.title(":green[Load & Revenue Performance 💰]")
st.markdown("---")

# --------------------------------------------------
# 2. DATA ENGINE
# --------------------------------------------------
data = load_all_tables()
data = apply_global_filters(data)

loads = data["loads"]
customers = data["customers"]
fuel = data["fuel_purchases"]

# Pre-processing
loads['load_date'] = pd.to_datetime(loads['load_date'], errors='coerce')
loads['Year'] = loads['load_date'].dt.year
loads['Month'] = loads['load_date'].dt.month

# --------------------------------------------------
# 3. KPI CALCULATIONS
# --------------------------------------------------
total_revenue = loads["revenue"].sum()
total_loads = loads["load_id"].nunique()
avg_revenue_per_load = total_revenue / total_loads if total_loads > 0 else 0
avg_weight = loads["weight_lbs"].mean()
fuel_surcharge = loads["fuel_surcharge"].sum() 
accessorial_charge = loads["accessorial_charge"].sum() 

#on_time_pct = (loads["delivery_status"] == "On Time").sum() / total_loads * 100 if "delivery_status" in loads.columns and total_loads > 0 else 0

on_time_pct = df['on_time_flag'].mean()

total_fuel_cost = fuel["total_cost"].sum()
profit_margin = ((total_revenue - total_fuel_cost) / total_revenue) * 100 if total_revenue > 0 else 0

# --------------------------------------------------
# 4. KPI DISPLAY
# --------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue", f"${total_revenue/1_000_000:.2f}M")
c2.metric("Avg Revenue / Load", f"${avg_revenue_per_load:,.0f}")
c3.metric("Total Loads", f"{total_loads:,}")
c4.metric("On-Time Delivery", f"{on_time_pct:.1f}%")

c5,  c8 = st.columns(2)
c5.metric("Avg Load Weight", f"{avg_weight:,.0f} lbs")
c8.metric("Profit Margin", f"{profit_margin:.1f}%")

st.markdown("---")

# --------------------------------------------------
# 5. VISUAL ANALYTICS (3-Column Layout)
# --------------------------------------------------
plt.rcParams['axes.facecolor'] = 'none'
col_a, col_b, col_c = st.columns(3)

with col_a:
    # 1. Revenue Share by Booking Type
    st.write("#### Revenue by Booking Type (%)")
    booking_rev = loads.groupby("booking_type")["revenue"].sum()
    fig1, ax1 = plt.subplots()
    ax1.pie(booking_rev, labels=booking_rev.index, autopct="%1.1f%%", colors=sns.color_palette("Pastel1"), startangle=140)
    st.pyplot(fig1)

    # 2. Total Customers by Type
    st.write("#### Customers by Segment")
    cust_type = customers["customer_type"].value_counts()
    fig2, ax2 = plt.subplots()
    ax2.pie(cust_type, labels=cust_type.index, autopct="%1.1f%%", colors=sns.color_palette("Set3"), startangle=140)
    st.pyplot(fig2)

with col_b:
    # 3. Revenue Distribution by Customer Status (Requested Logic)
    st.write("#### Revenue by Customer Status")
    load_customer_merge = loads.merge(customers, on='customer_id', how='left')
    rev_by_status = load_customer_merge.groupby('account_status')['revenue'].sum()
    fig3, ax3 = plt.subplots()
    ax3.pie(rev_by_status, labels=rev_by_status.index, autopct='%1.1f%%', colors=sns.color_palette("Pastel2"), startangle=90)
    st.pyplot(fig3)

    # 4. Revenue Share by Load Type
    st.write("#### Revenue Share by Load Type (%)")
    rev_share_load = (loads.groupby("load_type")["revenue"].sum() / total_revenue * 100).sort_values()
    fig4, ax4 = plt.subplots(figsize=(8, 6))
    ax4.barh(rev_share_load.index, rev_share_load.values, color=sns.color_palette("Blues", len(rev_share_load)))
    for i, v in enumerate(rev_share_load.values):
        ax4.text(v + 0.5, i, f"{v:.1f}%", va='center', fontweight='bold')
    sns.despine()
    st.pyplot(fig4)

with col_c:
    # 5. Customer Distribution by Status
    st.write("#### Customer Count by Status")
    cust_status_count = customers['account_status'].value_counts()
    fig5, ax5 = plt.subplots()
    ax5.pie(cust_status_count, labels=cust_status_count.index, autopct='%1.1f%%', colors=sns.color_palette("husl", len(cust_status_count)), startangle=90)
    st.pyplot(fig5)

# --------------------------------------------------
# 6. REVENUE SEASONALITY TREND (Full Width)
# --------------------------------------------------
st.markdown("---")
st.write("#### Revenue Seasonality Trend by Year")

monthly_revenue_data = loads.groupby(['Year', 'Month'])['revenue'].sum().reset_index().sort_values(['Year', 'Month'])


fig_trend, ax_trend = plt.subplots(figsize=(14, 5))
for year in monthly_revenue_data['Year'].unique():
    data_yr = monthly_revenue_data[monthly_revenue_data['Year'] == year]
    ax_trend.plot(data_yr['Month'], data_yr['revenue'], marker='o', label=str(year), linewidth=3)

plt.xticks(ticks=range(1,13), labels=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
plt.ylabel("Revenue ($)")
plt.legend(title="Year", frameon=False)
plt.grid(axis='y', linestyle='--', alpha=0.3)
sns.despine()
st.pyplot(fig_trend)

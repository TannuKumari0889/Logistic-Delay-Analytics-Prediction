import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_loader import load_all_tables
from src.filters import apply_global_filters

# --------------------------------------------------
# 1. PAGE CONFIG & LIGHT THEME (CSS)
# --------------------------------------------------
st.set_page_config(layout="wide", page_title="Load & Revenue Performance")

# Professional Light Theme with Green Accents
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

# Ensure datetime for seasonality
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
fuel_surcharge = loads["fuel_surcharge"].sum() if "fuel_surcharge" in loads.columns else 0
accessorial_charge = loads["accessorial_charge"].sum() if "accessorial_charge" in loads.columns else 0

# On-Time Delivery %
on_time_pct = (loads["delivery_status"] == "On Time").sum() / total_loads * 100 if "delivery_status" in loads.columns and total_loads > 0 else 0

# Profit Margin (Revenue - Fuel Cost)
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

c5, c6, c7, c8 = st.columns(4)
c5.metric("Avg Load Weight", f"{avg_weight:,.0f} lbs")
c6.metric("Fuel Surcharge", f"${fuel_surcharge/1_000_000:.2f}M")
c7.metric("Accessorial Charges", f"${accessorial_charge/1_000_000:.2f}M")
c8.metric("Profit Margin", f"{profit_margin:.1f}%")

st.markdown("---")

# --------------------------------------------------
# 5. VISUAL ANALYTICS (Light Pastel Palette)
# --------------------------------------------------
# Clean plot settings
plt.rcParams['axes.facecolor'] = 'none'
sns.set_context("talk", font_scale=0.8)

col_left, col_right = st.columns(2)

with col_left:
    # A. Revenue Share by Booking Type (Pie)
    st.write("#### Revenue Share by Booking Type (%)")
    booking_rev = loads.groupby("booking_type")["revenue"].sum()
    fig1, ax1 = plt.subplots(figsize=(6, 6))
    ax1.pie(booking_rev, labels=booking_rev.index, autopct="%1.1f%%", colors=sns.color_palette("Pastel1"), startangle=140)
    st.pyplot(fig1)

    # B. Revenue Share by Load Type (Horizontal Bar)
    st.write("#### Revenue Share by Load Type (%)")
    rev_share_load = (loads.groupby("load_type")["revenue"].sum() / total_revenue * 100).sort_values()
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    # Fixed Palette to "Blues"
    ax2.barh(rev_share_load.index, rev_share_load.values, color=sns.color_palette("Blues", len(rev_share_load)))
    for i, v in enumerate(rev_share_load.values):
        ax2.text(v + 0.5, i, f"{v:.1f}%", va='center', fontweight='bold')
    ax2.set_xlim(0, rev_share_load.max() + 10)
    sns.despine()
    st.pyplot(fig2)

with col_right:
    # C. Customer Distribution by Status (Pie)
    st.write("#### Customer Distribution by Status")
    cust_status = customers['account_status'].value_counts()
    fig3, ax3 = plt.subplots(figsize=(6, 6))
    ax3.pie(cust_status, labels=cust_status.index, autopct='%1.1f%%', colors=sns.color_palette("Pastel2"), startangle=90)
    st.pyplot(fig3)

    # D. Total Customers by Booking Type (Pie)
    st.write("#### Customers by Booking Segment (%)")
    cust_type = customers["customer_type"].value_counts()
    fig4, ax4 = plt.subplots(figsize=(6, 6))
    ax4.pie(cust_type, labels=cust_type.index, autopct="%1.1f%%", colors=sns.color_palette("Set3"), startangle=140)
    st.pyplot(fig4)

# --------------------------------------------------
# 6. FULL WIDTH TRENDS
# --------------------------------------------------
st.markdown("---")
st.write("#### Revenue Seasonality Trend by Year")

monthly_rev = loads.groupby(['Year', 'Month'])['revenue'].sum().reset_index().sort_values(['Year', 'Month'])

fig5, ax5 = plt.subplots(figsize=(14, 5))
for year in monthly_rev['Year'].unique():
    data_yr = monthly_rev[monthly_rev['Year'] == year]
    ax5.plot(data_yr['Month'], data_yr['revenue'], marker='o', label=str(year), linewidth=3)

plt.xticks(ticks=range(1,13), labels=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
plt.ylabel("Revenue ($)")
plt.legend(title="Year", frameon=False)
plt.grid(axis='y', linestyle='--', alpha=0.3)
sns.despine()
st.pyplot(fig5)

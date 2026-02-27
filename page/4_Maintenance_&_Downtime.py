import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_loader import load_all_tables
from src.filters import apply_global_filters


# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------
st.title(":green[Maintenance & Downtime 🛠️]")


# --------------------------------------------------
# LOAD + FILTER DATA
# --------------------------------------------------
data = load_all_tables()
data = apply_global_filters(data)

maintenance = data["maintenance_records"]
trucks = data["trucks"]


# --------------------------------------------------
# KPI CALCULATIONS (Dynamic)
# --------------------------------------------------

total_cost = maintenance["total_cost"].sum()
total_downtime = maintenance["downtime_hours"].sum()

total_trucks = trucks["truck_id"].nunique()

avg_downtime_per_truck = (
    total_downtime / total_trucks if total_trucks > 0 else 0
)

avg_cost_per_truck = (
    total_cost / total_trucks if total_trucks > 0 else 0
)

# Truck with highest maintenance cost
cost_by_truck = (
    maintenance.groupby("truck_id")["total_cost"]
    .sum()
    .reset_index()
)

if not cost_by_truck.empty:
    high_cost_truck = cost_by_truck.sort_values(
        "total_cost", ascending=False
    ).iloc[0]["truck_id"]
else:
    high_cost_truck = "N/A"


# --------------------------------------------------
# KPI DISPLAY
# --------------------------------------------------

col1, col2, col3 = st.columns(3)
col1.metric("Total Maintenance Cost", f"${total_cost/1_000_000:.2f}M")
col2.metric("Total Downtime Hours", f"{total_downtime:,.0f}")
col3.metric("Avg Downtime per Truck", f"{avg_downtime_per_truck:.2f}")

col1, col2 = st.columns(2)
col1.metric("High Maintenance Cost Truck", high_cost_truck)
col2.metric("Avg Maintenance Cost per Truck", f"${avg_cost_per_truck/1_000:.2f}K")


# ==================================================
# Maintenance Type Distribution
# ==================================================

maint_dist = (
    maintenance["maintenance_type"]
    .value_counts(normalize=True) * 100
)

fig, ax = plt.subplots(figsize=(8, 4))

sns.barplot(
    x=maint_dist.index,
    y=maint_dist.values,
    ax=ax
)

ax.set_title("Maintenance Type Distribution (%)")
ax.set_xlabel("Maintenance Type")
ax.set_ylabel("Percentage")

for i, val in enumerate(maint_dist.values):
    ax.text(i, val + 1, f"{val:.1f}%", ha="center")

plt.xticks(rotation=30)
st.pyplot(fig)

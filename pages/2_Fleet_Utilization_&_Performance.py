import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
 
from src.data_loader import load_all_tables
from src.filters import apply_global_filters
 
 
# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.title(":green[Fleet Utilization & Performance ⚡]")
 
 
# --------------------------------------------------
# LOAD + FILTER DATA
# --------------------------------------------------
data = load_all_tables()
data = apply_global_filters(data)
 
trucks = data["trucks"]
trips = data["trips"]
trailers = data["trailers"]
fuel_purchases = data["fuel_purchases"]
truck_util = data["truck_utilization_metrics"]
maintenance = data["maintenance_records"]
 
 
# --------------------------------------------------
# KPI SECTION (Dynamic — No Hardcoding)
# --------------------------------------------------
 
total_trucks = trucks["truck_id"].nunique()
active_trucks = trucks[trucks["status"] == "Active"]["truck_id"].nunique()
avg_util = truck_util["utilization_rate"].mean()
total_trips = trips["trip_id"].nunique()
total_miles = trips["actual_distance_miles"].sum()
total_downtime = maintenance["downtime_hours"].sum()
maintenance_count = maintenance["maintenance_id"].nunique()
 
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Utilization Rate", f"{avg_util:.2%}")
col2.metric("Total Miles Driven", f"{total_miles:,.0f}")
col3.metric("Total Trips", f"{total_trips:,}")
col4.metric("Total Trucks", total_trucks)
 
col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Trucks", active_trucks)
col2.metric("Total Downtime Hours", f"{total_downtime:,.0f}")
col3.metric("Maintenance Events", maintenance_count)
col4.metric("Avg Trips per Truck", f"{total_trips/total_trucks:.2f}")
 
 
# ==================================================
# 1️⃣ Fleet Utilization Distribution
# ==================================================
 
def categorize_util(x):
    if x < 0.7:
        return "Underutilized"
    elif x <= 1:
        return "Optimal"
    return "Overutilized"
 
truck_util["category"] = truck_util["utilization_rate"].apply(categorize_util)
 
util_dist = truck_util["category"].value_counts(normalize=True) * 100
 
fig1, ax1 = plt.subplots(figsize=(5, 5))
ax1.pie(util_dist, labels=util_dist.index, autopct="%1.1f%%")
ax1.set_title("Fleet Utilization Distribution (%)")
st.pyplot(fig1)
 
 
# ==================================================
# 2️⃣ Truck Status Distribution
# ==================================================
 
status_dist = trucks["status"].value_counts(normalize=True) * 100
 
fig2, ax2 = plt.subplots(figsize=(6, 4))
sns.barplot(x=status_dist.index, y=status_dist.values, ax=ax2)
 
ax2.set_ylabel("Percentage")
ax2.set_xlabel("Truck Status")
ax2.set_title("Truck Status Distribution (%)")
 
for i, val in enumerate(status_dist.values):
    ax2.text(i, val + 1, f"{val:.1f}%", ha="center")
 
st.pyplot(fig2)
 
 
# ==================================================
# 3️⃣ Trip Distribution by Trailer Age
# ==================================================
 
CURRENT_YEAR = 2025
trailers["age"] = CURRENT_YEAR - trailers["model_year"]
trailers = trailers[trailers["age"] <= 10]
 
trailers["age_group"] = pd.cut(
    trailers["age"],
    bins=[0, 3, 7, 10],
    labels=["0-3 Years", "4-7 Years", "8-10 Years"]
)
 
merged = trips.merge(
    trailers[["trailer_id", "age_group"]],
    on="trailer_id",
    how="inner"
)
 
age_dist = (
    merged.groupby("age_group")["trip_id"]
    .count()
    .reset_index(name="total_trips")
)
 
age_dist["percentage"] = (
    age_dist["total_trips"] /
    age_dist["total_trips"].sum()
) * 100
 
fig3, ax3 = plt.subplots(figsize=(6, 4))
sns.barplot(data=age_dist, x="age_group", y="percentage", ax=ax3)
 
ax3.set_title("Trip Distribution by Trailer Age (%)")
ax3.set_ylabel("Percentage")
 
for i, row in age_dist.iterrows():
    ax3.text(i, row["percentage"] + 0.5, f"{row['percentage']:.1f}%", ha="center")
 
st.pyplot(fig3)
 
 
# ==================================================
# 4️⃣ Fuel Cost by Trailer Type
# ==================================================
 
fuel_merge = (
    fuel_purchases
    .merge(trips[["trip_id", "trailer_id"]], on="trip_id", how="left")
    .merge(trailers[["trailer_id", "trailer_type"]], on="trailer_id", how="left")
)
 
fuel_by_type = (
    fuel_merge.groupby("trailer_type")["total_cost"]
    .sum()
    .reset_index()
    .sort_values("total_cost", ascending=False)
)
 
fuel_by_type["percentage"] = (
    fuel_by_type["total_cost"] /
    fuel_by_type["total_cost"].sum()
) * 100
 
fig4, ax4 = plt.subplots(figsize=(8, 5))
sns.barplot(
    data=fuel_by_type,
    x="trailer_type",
    y="total_cost",
    palette="viridis",
    ax=ax4
)
 
ax4.set_title("Total Fuel Cost by Trailer Type")
ax4.set_ylabel("Total Fuel Cost ($)")
ax4.set_xlabel("Trailer Type")
plt.xticks(rotation=45)
 
for i, row in fuel_by_type.iterrows():
    ax4.text(i, row["total_cost"], f"{row['percentage']:.1f}%", ha="center")
 
st.pyplot(fig4)

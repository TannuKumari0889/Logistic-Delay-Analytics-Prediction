import streamlit as st

# If the user hasn't logged in on the main page, stop them here
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("Please log in on the Home page to access this dashboard.")
    st.stop()


import sys
import os
import pandas as pd
import datetime
from model_loader import load_assets

# Setup
st.set_page_config(page_title="Logistics Risk Dashboard", layout="wide")
st.title("🚚 Logistics On-Time Prediction Dashboard")
st.markdown("---")

# Load assets from engine
model, preprocessor, top_9_features, ui_options, base_cols = load_assets

# --- UI LOGIC: Define what to show/hide ---
display_cols = list(base_cols)

# Add categories you specifically WANT to see
manual_add = ["load_type", "booking_type"] 
for col in manual_add:
    if col not in display_cols:
        display_cols.append(col)

with st.form("prediction_form"):
    st.subheader("Trip Parameters")
    user_input = {}
    col1, col2 = st.columns(2)
    
    visible_index = 0
    for col_name in display_cols:
        
        # 1. SILENT: Fuel Surcharge (Hidden)
        if col_name == "fuel_surcharge_rate":
            user_input[col_name] = 0.0
            continue
            
        # 2. SILENT: Vehicle Type (Hidden)
        if col_name == "vehicle_type":
            user_input[col_name] = ui_options[col_name][0] if col_name in ui_options else "Unknown"
            continue
            
        # 3. SILENT: Dispatch Date (Hidden - uses today's date)
        if any(x in col_name for x in ["_year", "_month", "_day", "dayofweek"]):
            if "date_handled" not in user_input:
                today = datetime.date.today()
                user_input.update({
                    'dispatch_date_year': today.year, 
                    'dispatch_date_month': today.month,
                    'dispatch_date_day': today.day, 
                    'dispatch_date_dayofweek': today.weekday(),
                    'date_handled': True
                })
            continue

        # --- VISIBLE INPUTS ---
        slot = col1 if visible_index % 2 == 0 else col2
        visible_index += 1
        
        label = col_name.replace('_', ' ').title()
        
        if col_name in ui_options:
            user_input[col_name] = slot.selectbox(f"Select {label}", options=ui_options[col_name])
        else:
            user_input[col_name] = slot.number_input(f"Enter {label}", value=0.0)

    submit = st.form_submit_button("Analyze Delivery Risk", type="primary")

# Calculation Logic
if submit:
    # 1. Create raw dataframe
    input_df = pd.DataFrame([user_input])
    
    # 2. Fill missing columns for preprocessor
    for col in preprocessor.feature_names_in_:
        if col not in input_df.columns:
            if col in preprocessor.transformers_[0][2]:
                input_df[col] = 0
            else:
                input_df[col] = "Unknown"

    # 3. Transform via Pipeline
    transformed_df = pd.DataFrame(
        preprocessor.transform(input_df), 
        columns=preprocessor.get_feature_names_out()
    )
    
    # 4. Create Ghost Table (matches model training shape)
    model_features = model.feature_names_in_
    final_input = pd.DataFrame(0, index=[0], columns=model_features)
    
    # Fill only the features we have
    for col in top_9_features:
        if col in transformed_df.columns:
            final_input[col] = transformed_df[col].values

    # 5. Predict
    prediction = model.predict(final_input)[0]
    prob = model.predict_proba(final_input)[0][1]

    st.markdown("### Prediction Result:")
    if prediction == 1:
        st.success(f"✅ **ON TIME** (Probability: {prob:.1%})")
    else:
        st.error(f"⚠️ **POTENTIAL DELAY** (Risk Level: {(1-prob):.1%})")

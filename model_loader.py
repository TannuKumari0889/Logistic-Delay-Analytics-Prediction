import joblib
import json
import streamlit as st

@st.cache_resource
def load_assets():  # <--- Make sure this name is EXACTLY 'load_assets'
    model = joblib.load("final_model.pkl")
    preprocessor = joblib.load("preprocessor.pkl")
    important_features = joblib.load("important_features.pkl")[:9]
    
    with open("ui_options.json", "r") as f:
        ui_options = json.load(f)
        
    base_cols = []
    for feat in important_features:
        found = False
        for cat in ui_options.keys():
            if f"cat__{cat}" in feat:
                if cat not in base_cols: base_cols.append(cat)
                found = True
        if not found and "num__" in feat:
            num_name = feat.replace("num__", "")
            if num_name not in base_cols: base_cols.append(num_name)
            
    return model, preprocessor, important_features, ui_options, base_cols
import streamlit as st

st.set_page_config(layout="wide")

st.title("🚛 Logistic Operations Analytics")

st.markdown("### Welcome to the Fleet Intelligence Dashboard")

st.write(
    """
    This dashboard provides end-to-end analytics across:

    • Executive Overview 
    • Fleet Utilization & Performance 
    • Fuel Cost & Efficiency  
    • Maintenance & Downtime  
    • Load & Revenue Performance  
    • Route & Trip Efficiency 
    • Driver Performance  
    • Safety & Risk  

    Use the sidebar to navigate between different dashboards.
    """
)

st.info("👈 Select a page from the sidebar to begin.")

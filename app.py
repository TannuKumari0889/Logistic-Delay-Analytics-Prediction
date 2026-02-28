import streamlit as st

st.set_page_config(layout="wide")

# 1. Initialize authentication state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# 2. Login Logic
if not st.session_state["authenticated"]:
    st.title("🔒 CEO Login")
    
    with st.form("login_form"):
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        submit = st.form_submit_id("Login")
        
        if submit:
            if user == "CEO" and pw == "CEO@1234":
                st.session_state["authenticated"] = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid Username or Password")
    
    st.stop() # Prevents the rest of the page from loading

# 3. Sidebar Logout (Optional but recommended)
if st.sidebar.button("Log Out"):
    st.session_state["authenticated"] = False
    st.rerun()

# --- YOUR ORIGINAL CONTENT STARTS HERE ---
st.title("🚛 Logistic Operations Analytics")
st.markdown("### Welcome to the Fleet Intelligence Dashboard")

st.write(
    """
    This dashboard provides end-to-end analytics across:
    • Executive Overview 
    • Fleet & Fuel Analytics
    • Load & Revenue Performance  
    • Driver Performance   
    • Safety & Risk  
    • Trip Delay Prediction
    
    Use the sidebar to navigate between different dashboards.
    """
)

st.info("👈 Select a page from the sidebar to begin.")

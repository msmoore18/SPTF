import streamlit as st
import pandas as pd
import plotly.express as px
import msoffcrypto
import io

st.set_page_config(layout="wide")

def load_data(password):
    file_path = "SPTF_Count.xlsx"
    try:
        with open(file_path, "rb") as file:
            decrypted = io.BytesIO()
            office_file = msoffcrypto.OfficeFile(file)
            if not office_file.is_encrypted():
                return pd.read_excel(file_path)
            office_file.load_key(password)
            office_file.decrypt(decrypted)
            return pd.read_excel(decrypted)
    except Exception:
        return None

if "data" not in st.session_state:
    st.title("Enter Password to Access Data")
    def submit_password():
        password = st.session_state.password_input
        if password:
            data = load_data(password)
            if data is None:
                st.session_state["password_error"] = True
            else:
                st.session_state["data"] = data
                st.session_state["password_error"] = False

    st.text_input("Excel File Password:", type="password", key="password_input", on_change=submit_password)
    if st.button("Enter"):
        submit_password()
    if st.session_state.get("password_error"):
        st.error("Incorrect password or file issue. Please try again.")
    elif "data" in st.session_state:
        st.rerun()
    st.stop()

data = st.session_state["data"].copy()

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Lot Map", "Tree Inventory", "Projected Tree Inventory", "Tree Maintenance"])

if "new_trees" not in st.session_state:
    st.session_state["new_trees"] = 0

def project_tree_growth(data, years=10, new_trees_per_year=0):
    projections = []
    for year in range(0, years + 1):
        year_data = data.copy()
        year_data["Year"] = 2025 + year
        
        # Correct tree growth logic
        def grow_tree(height, years):
            if height < 2:
                height = min(2, height + 0.5 * years)  # Grow 0.5ft per year until 2ft
            if height >= 2:
                height += max(0, years - (2 - height) * 2)  # After reaching 2ft, grow 1ft per year
            return height
        
        year_data["Tree Height (ft)"] = year_data["Tree Height (ft)"].apply(lambda x: grow_tree(x, year))
        
        # Ensure new trees continue growing after reaching 2ft
        new_trees = []
        for yr i

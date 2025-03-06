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


if page == "Projected Tree Inventory":
    st.title("Projected Tree Inventory")
    
    new_trees_per_year = st.number_input("How many 6-inch trees to add per year?", min_value=0, step=1, value=st.session_state["new_trees"])
    st.session_state["new_trees"] = new_trees_per_year
    
    if st.button("Calculate"):
        projected_data = project_tree_growth(data, years=10, new_trees_per_year=st.session_state["new_trees"])
        summary_data = create_summary(projected_data)
        st.session_state["summary_data"] = summary_data
    
    if "summary_data" in st.session_state:
        st.dataframe(st.session_state["summary_data"])

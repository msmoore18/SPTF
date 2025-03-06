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

data = st.session_state["data"]

def project_tree_growth(data, years=10):
    projection = data.copy()
    for year in range(1, years + 1):
        projection[f'Year {2025 + year}'] = projection['Tree Height (ft)'].apply(lambda x: x + 1 if x > 2 else x + 0.5)
    return projection

def update_with_new_trees(projection, years=10, new_trees_per_year=0):
    new_tree_entries = []
    for year in range(1, years + 1):
        new_tree_entries.append({
            'Tree Height (ft)': 0.5,
            f'Year {2025 + year}': 0.5,
            'Lot': 'N/A',
            'Row': 'N/A',
            'Quality': 'N/A',
            'Count': new_trees_per_year
        })
    return pd.concat([projection, pd.DataFrame(new_tree_entries)], ignore_index=True)

def apply_sales(projection, years=10, sales={}):
    for year_col in sales:
        if year_col in projection.columns:
            projection[year_col] = projection[year_col] - sales[year_col]
            projection[year_col] = projection[year_col].clip(lower=0)
    return projection

def create_summary(projection, years=10):
    summary = projection.groupby("Tree Height (ft)")[[f'Year {2025 + i}' for i in range(1, years + 1)]].sum().reset_index()
    return summary

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Lot Map", "Tree Inventory", "Projected Tree Inventory", "Tree Maintenance"])

if page == "Projected Tree Inventory":
    st.title("Projected Tree Inventory")
    projected_data = project_tree_growth(data)
    new_trees_per_year = st.number_input("How many 6-inch trees to add per year?", min_value=0, step=1)
    projected_data = update_with_new_trees(projected_data, new_trees_per_year=new_trees_per_year)
    
    st.subheader("Specify Sales Numbers")
    sales = {}
    for year in range(1, 11):
        sales[f'Year {2025 + year}'] = st.number_input(f"Trees to sell in {2025 + year}", min_value=0, step=1)
    projected_data = apply_sales(projected_data, sales=sales)
    
    summary_data = create_summary(projected_data)
    st.dataframe(summary_data)

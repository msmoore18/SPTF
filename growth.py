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

if "data" in st.session_state:
    data = st.session_state["data"].copy()
else:
    st.error("Data not loaded. Please enter the correct password.")
    st.stop()

st.sidebar.title("Navigation")
st.sidebar.radio("Go to", ["Lot Map", "Tree Inventory", "Projected Tree Inventory", "Tree Maintenance"])

def project_tree_inventory(data, years=20, new_trees_per_year=0, sell_trees={}):
    projections = []
    for year in range(0, years + 1):
        year_data = data.copy()
        year_data["Year"] = 2025 + year
        
        # Remove sold trees each year
        if year > 0:
            for height, count in sell_trees.items():
                year_data.loc[year_data["Tree Height (ft)"] == height, "Count"] -= count
                year_data["Count"] = year_data["Count"].clip(lower=0)
        
        # Add new trees each year with a fixed height
        new_trees = pd.DataFrame({
            "Tree Height (ft)": [0.5] * new_trees_per_year,  # Fixed height of 6 inches
            "Year": [2025 + year] * new_trees_per_year,
            "Lot": ["N/A"] * new_trees_per_year,
            "Row": ["N/A"] * new_trees_per_year,
            "Quality": ["N/A"] * new_trees_per_year,
            "Count": [1] * new_trees_per_year
        })

        year_data = pd.concat([year_data, new_trees], ignore_index=True)
        projections.append(year_data)
    return pd.concat(projections)

def create_summary(projection):
    summary = projection.groupby(["Tree Height (ft)", "Year"])['Count'].sum().unstack(fill_value=0).reset_index()
    summary_melted = projection.groupby(["Tree Height (ft)", "Year"])['Count'].sum().reset_index()
    return summary, summary_melted

if "Projected Tree Inventory" in st.sidebar.radio("Navigation", ["Lot Map", "Tree Inventory", "Projected Tree Inventory", "Tree Maintenance"]):
    st.title("Projected Tree Inventory")

    if "new_trees" not in st.session_state:
        st.session_state["new_trees"] = 0

    new_trees_per_year = st.number_input("How many 6-inch trees to add per year?", min_value=0, step=1, value=st.session_state["new_trees"])
    st.session_state["new_trees"] = new_trees_per_year
    
    st.write("Enter the number of trees to sell each year by height:")
    sell_trees = {}
    for height in sorted(data["Tree Height (ft)"].unique()):
        sell_trees[height] = st.number_input(f"Sell {int(height)} ft trees per year:", min_value=0, step=1, value=0, key=f"sell_{height}")
    
    if st.button("Calculate"):
        projected_data = project_tree_inventory(data, years=20, new_trees_per_year=st.session_state["new_trees"], sell_trees=sell_trees)
        summary_data, summary_melted = create_summary(projected_data)
        st.session_state["summary_data"] = summary_data
        st.session_state["summary_melted"] = summary_melted

    if "summary_data" in st.session_state:
        st.dataframe(st.session_state["summary_data"])
        
        fig = px.line(st.session_state["summary_melted"], x="Year", y="Count", color="Tree Height (ft)", 
                      labels={"Year": "Year", "Count": "Tree Count", "Tree Height (ft)": "Tree Height (ft)"},
                      title="Projected Tree Inventory Over Time")
        st.plotly_chart(fig)

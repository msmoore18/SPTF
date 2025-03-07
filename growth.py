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

def project_tree_growth(data, years=10, new_trees_per_year=0, trees_sold_per_year=0):
    projections = []
    height_distribution = {h: data[data["Tree Height (ft)"] == h]["Count"].sum() for h in range(1, 21)}
    
    for year in range(0, years + 1):
        year_data = []
        for height in range(20, 0, -1):
            next_height = height + 1
            count = height_distribution.get(height, 0)
            
            if height == 10 and year > 0:
                count = max(0, height_distribution.get(10, 0) - trees_sold_per_year)
            elif height >= 11 and year > 0:
                count = max(0, height_distribution.get(height - 1, 0))
            
            year_data.append({
                "Tree Height (ft)": height,
                "Year": 2025 + year,
                "Lot": "N/A",
                "Row": "N/A",
                "Quality": "N/A",
                "Count": count
            })
        
        year_data.append({
            "Tree Height (ft)": 0,
            "Year": 2025 + year,
            "Lot": "N/A",
            "Row": "N/A",
            "Quality": "N/A",
            "Count": new_trees_per_year
        })
        
        height_distribution = {entry["Tree Height (ft)"]: entry["Count"] for entry in year_data}
        projections.extend(year_data)
    
    return pd.DataFrame(projections)

def create_summary(projection, years=10):
    projection["Tree Height (ft)"] = projection["Tree Height (ft)"].apply(lambda x: int(x))
    summary = projection.groupby(["Tree Height (ft)", "Year"])['Count'].sum().unstack(fill_value=0).reset_index()
    summary_melted = projection.groupby(["Tree Height (ft)", "Year"])['Count'].sum().reset_index()
    return summary, summary_melted

if "Projected Tree Inventory" in st.sidebar.radio("Navigation", ["Lot Map", "Tree Inventory", "Projected Tree Inventory", "Tree Maintenance"]):
    st.title("Projected Tree Inventory")

    if "new_trees" not in st.session_state:
        st.session_state["new_trees"] = 0
    if "trees_sold" not in st.session_state:
        st.session_state["trees_sold"] = 0

    new_trees_per_year = st.number_input("How many 6-inch trees to add per year?", min_value=0, step=1, value=st.session_state["new_trees"])
    trees_sold_per_year = st.number_input("How many 10ft trees to sell per year?", min_value=0, step=1, value=st.session_state["trees_sold"])
    
    st.session_state["new_trees"] = new_trees_per_year
    st.session_state["trees_sold"] = trees_sold_per_year

    if st.button("Calculate"):
        projected_data = project_tree_growth(data, years=10, new_trees_per_year=new_trees_per_year, trees_sold_per_year=trees_sold_per_year)
        summary_data, summary_melted = create_summary(projected_data)
        st.session_state["summary_data"] = summary_data
        st.session_state["summary_melted"] = summary_melted

    if "summary_data" in st.session_state:
        st.dataframe(st.session_state["summary_data"])

        fig = px.line(st.session_state["summary_melted"], x="Year", y="Count", color="Tree Height (ft)", 
                      labels={"Year": "Year", "Count": "Tree Count", "Tree Height (ft)": "Tree Height (ft)"},
                      title="Projected Tree Growth Over Time")
        st.plotly_chart(fig)


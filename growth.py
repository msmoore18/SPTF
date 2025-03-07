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

def project_tree_growth(data, years=10, new_trees_per_year=0, trees_sold_2025=0):
    projections = []
    for year in range(0, years + 1):
        year_data = data.copy()
        year_data["Year"] = 2025 + year
        year_data["Tree Height (ft)"] += year  # Grow all trees 1ft per year
        
        # Subtract sold 6ft trees in 2025
        if year == 0:
            year_data.loc[(year_data["Tree Height (ft)"] == 6), "Count"] -= trees_sold_2025
            year_data["Count"] = year_data["Count"].clip(lower=0)  # Ensure no negative values
        
        # Add new trees each year, all starting at <1ft and growing annually
        new_trees = pd.DataFrame({
            "Tree Height (ft)": [0 + y for y in range(year + 1)],  # Trees added every year and grow
            "Year": [2025 + year] * (year + 1),
            "Lot": ["N/A"] * (year + 1),
            "Row": ["N/A"] * (year + 1),
            "Quality": ["N/A"] * (year + 1),
            "Count": [new_trees_per_year] * (year + 1)
        })
        
        year_data = pd.concat([year_data, new_trees], ignore_index=True)
        projections.append(year_data)
    return pd.concat(projections)

def create_summary(projection, years=10):
    projection["Tree Height (ft)"] = projection["Tree Height (ft)"].apply(lambda x: int(x))  # Bin tree heights to whole numbers
    summary = projection.groupby(["Tree Height (ft)", "Year"])['Count'].sum().unstack(fill_value=0).reset_index()
    summary_melted = projection.groupby(["Tree Height (ft)", "Year"])['Count'].sum().reset_index()  # For the plot
    return summary, summary_melted

if "Projected Tree Inventory" in st.sidebar.radio("Navigation", ["Lot Map", "Tree Inventory", "Projected Tree Inventory", "Tree Maintenance"]):
    st.title("Projected Tree Inventory")
    
    if "new_trees" not in st.session_state:
        st.session_state["new_trees"] = 0
    if "trees_sold_2025" not in st.session_state:
        st.session_state["trees_sold_2025"] = 0
    
    new_trees_per_year = st.number_input("How many 6-inch trees to add per year?", min_value=0, step=1, value=st.session_state["new_trees"])
    st.session_state["new_trees"] = new_trees_per_year
    
    trees_sold_2025 = st.slider("How many 6ft trees to sell in 2025?", min_value=0, max_value=1000, step=1, value=st.session_state["trees_sold_2025"])
    st.session_state["trees_sold_2025"] = trees_sold_2025
    
    if st.button("Calculate"):
        projected_data = project_tree_growth(data, years=10, new_trees_per_year=st.session_state["new_trees"], trees_sold_2025=st.session_state["trees_sold_2025"])
        summary_data, summary_melted = create_summary(projected_data)
        st.session_state["summary_data"] = summary_data
        st.session_state["summary_melted"] = summary_melted
    
    if "summary_data" in st.session_state:
        st.dataframe(st.session_state["summary_data"])  # Display summary table correctly
        
        # Create a line plot using the melted summary data
        fig = px.line(st.session_state["summary_melted"], x="Year", y="Count", color="Tree Height (ft)", 
                      labels={"Year": "Year", "Count": "Tree Count", "Tree Height (ft)": "Tree Height (ft)"},
                      title="Projected Tree Growth Over Time")
        st.plotly_chart(fig)

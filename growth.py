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

def project_tree_growth_updated(data, years=20, new_trees_per_year=0, trees_sold_per_height=None):
    projections = []
    if trees_sold_per_height is None:
        trees_sold_per_height = [0] * 26  # Default to no sales for 26 height levels

    for year in range(0, years + 1):
        year_data = data.copy()
        year_data["Year"] = 2025 + year
        year_data["Tree Height (ft)"] += year

        new_trees = pd.DataFrame({
            "Tree Height (ft)": [0],
            "Year": [2025 + year],
            "Lot": ["N/A"],
            "Row": ["N/A"],
            "Quality": ["N/A"],
            "Count": [new_trees_per_year]
        })

        # Ensure trees are removed correctly based on height
        for height, trees_sold in enumerate(trees_sold_per_height):
            height_filter = year_data["Tree Height (ft)"] == height
            available_trees = year_data.loc[height_filter, "Count"].sum()
            if available_trees > 0:
                trees_to_remove = min(trees_sold, available_trees)
                year_data.loc[height_filter, "Count"] -= trees_to_remove
                year_data.loc[year_data["Count"] < 0, "Count"] = 0  # Prevent negative values

        year_data = pd.concat([year_data, new_trees], ignore_index=True)
        projections.append(year_data)

    return pd.concat(projections)

def create_summary(projection, years=20):
    projection["Tree Height (ft)"] = projection["Tree Height (ft)"].apply(lambda x: int(x))
    summary = projection.groupby(["Tree Height (ft)", "Year"])["Count"].sum().unstack(fill_value=0).reset_index()
    summary_melted = projection.groupby(["Tree Height (ft)", "Year"])["Count"].sum().reset_index()
    return summary, summary_melted

if "Projected Tree Inventory" in st.sidebar.radio("Navigation", ["Lot Map", "Tree Inventory", "Projected Tree Inventory", "Tree Maintenance"]):
    st.title("Projected Tree Inventory")

    if "new_trees" not in st.session_state:
        st.session_state["new_trees"] = 1000  # Default from Excel P1

    new_trees_per_year = st.number_input("How many 6-inch trees to add per year?", min_value=0, step=1, value=st.session_state["new_trees"])
    st.session_state["new_trees"] = new_trees_per_year

    trees_sold_per_height = []
    st.subheader("Enter Number of Trees to Sell Per Tree Height")
    for height in range(26):
        trees_sold = st.number_input(f"Tree Height {height}", min_value=0, step=1, key=f"trees_sold_{height}")
        trees_sold_per_height.append(trees_sold)

    if st.button("Calculate"):
        projected_data = project_tree_growth_updated(data, years=10, new_trees_per_year=st.session_state["new_trees"], trees_sold_per_height=trees_sold_per_height)
        summary_data, summary_melted = create_summary(projected_data)
        st.session_state["summary_data"] = summary_data
        st.session_state["summary_melted"] = summary_melted

    if "summary_data" in st.session_state:
        st.dataframe(st.session_state["summary_data"])
        fig = px.line(st.session_state["summary_melted"], x="Year", y="Count", color="Tree Height (ft)", 
                      labels={"Year": "Year", "Count": "Tree Count", "Tree Height (ft)": "Tree Height (ft)"},
                      title="Projected Tree Growth Over Time")
        st.plotly_chart(fig)

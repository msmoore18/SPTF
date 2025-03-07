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
page = st.sidebar.radio("Go to", ["Lot Map", "Tree Inventory", "Projected Tree Inventory", "Tree Maintenance"])

def project_tree_growth(data, years=20, new_trees_per_year=0, trees_sold_per_year=0):
    projections = []
    
    # Create a copy of the dataset to modify year by year
    for year in range(0, years + 1):
        year_data = data.copy()
        year_data["Year"] = 2025 + year
        year_data["Tree Height (ft)"] += year  # Grow trees 1ft per year

        # Adjust for trees sold
        if year > 0:  # Start selling trees from year 1 (2025)
            prev_year = projections[-1]
            if 6 in prev_year["Tree Height (ft)"].values:
                available_6ft_trees = prev_year.loc[prev_year["Tree Height (ft)"] == 6, "Count"].values[0]
                trees_to_sell = min(trees_sold_per_year, available_6ft_trees)

                # Reduce the number of 6ft trees in the current year
                year_data.loc[year_data["Tree Height (ft)"] == 6, "Count"] -= trees_to_sell

                # Ensure non-negative count
                year_data["Count"] = year_data["Count"].apply(lambda x: max(x, 0))

        # Add new trees each year
        new_trees = pd.DataFrame({
            "Tree Height (ft)": list(range(year + 1)),  # New trees start at 0ft and grow
            "Year": [2025 + year] * (year + 1),
            "Lot": ["N/A"] * (year + 1),
            "Row": ["N/A"] * (year + 1),
            "Quality": ["N/A"] * (year + 1),
            "Count": [new_trees_per_year] * (year + 1)
        })

        year_data = pd.concat([year_data, new_trees], ignore_index=True)
        projections.append(year_data)

    return pd.concat(projections)

def create_summary(projection):
    projection["Tree Height (ft)"] = projection["Tree Height (ft)"].astype(int)  # Bin heights to whole numbers
    summary = projection.groupby(["Tree Height (ft)", "Year"])["Count"].sum().unstack(fill_value=0).reset_index()
    summary_melted = projection.groupby(["Tree Height (ft)", "Year"])["Count"].sum().reset_index()
    return summary, summary_melted

if page == "Projected Tree Inventory":
    st.title("Projected Tree Inventory")

    # Ensure new_trees_per_year and trees_sold_per_year are stored in session state
    if "new_trees" not in st.session_state:
        st.session_state["new_trees"] = 0
    if "trees_sold" not in st.session_state:
        st.session_state["trees_sold"] = 0

    new_trees_per_year = st.number_input("How many 6-inch trees to add per year?", min_value=0, step=1, value=st.session_state["new_trees"])
    trees_sold_per_year = st.number_input("How many 6ft trees to sell per year?", min_value=0, step=1, value=st.session_state["trees_sold"])

    # Update session state only when necessary
    if new_trees_per_year != st.session_state["new_trees"]:
        st.session_state["new_trees"] = new_trees_per_year
    if trees_sold_per_year != st.session_state["trees_sold"]:
        st.session_state["trees_sold"] = trees_sold_per_year

    if st.button("Calculate"):
        projected_data = project_tree_growth(
            data, years=20, new_trees_per_year=st.session_state["new_trees"], trees_sold_per_year=st.session_state["trees_sold"]
        )
        summary_data, summary_melted = create_summary(projected_data)

        # Store results in session state
        st.session_state["summary_data"] = summary_data
        st.session_state["summary_melted"] = summary_melted

    # Display results if available
    if "summary_data" in st.session_state:
        st.dataframe(st.session_state["summary_data"])

        # Line chart visualization
        fig = px.line(
            st.session_state["summary_melted"], x="Year", y="Count", color="Tree Height (ft)", 
            labels={"Year": "Year", "Count": "Tree Count", "Tree Height (ft)": "Tree Height (ft)"},
            title="Projected Tree Growth Over Time (with Sales Impact)"
        )
        st.plotly_chart(fig)

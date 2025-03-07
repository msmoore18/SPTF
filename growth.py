import streamlit as st
import pandas as pd
import plotly.express as px
import msoffcrypto
import io

st.set_page_config(layout="wide")

# Function to load Excel data
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

# Initialize session state variables
if "data" not in st.session_state:
    st.session_state["data"] = None
if "password_error" not in st.session_state:
    st.session_state["password_error"] = False

# **Password entry screen**
if st.session_state["data"] is None:
    st.title("Enter Password to Access Data")

    password = st.text_input("Excel File Password:", type="password", key="password_input")

    if st.button("Enter"):
        if password:
            data = load_data(password)
            if data is None:
                st.session_state["password_error"] = True
            else:
                st.session_state["data"] = data
                st.session_state["password_error"] = False
                st.rerun()  # Reload the app with data

    # Display error message if the password is incorrect
    if st.session_state["password_error"]:
        st.error("Incorrect password or file issue. Please try again.")

    st.stop()  # Stop execution until the correct password is entered

# Load the data into a local variable
data = st.session_state["data"].copy()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Lot Map", "Tree Inventory", "Projected Tree Inventory", "Tree Maintenance"])

# **Projected Tree Inventory Page**
if page == "Projected Tree Inventory":
    st.title("Projected Tree Inventory")

    # Ensure new_trees_per_year is stored in session state
    if "new_trees" not in st.session_state:
        st.session_state["new_trees"] = 0

    new_trees_per_year = st.number_input("How many 6-inch trees to add per year?", min_value=0, step=1, value=st.session_state["new_trees"])
    
    # Update session state only when necessary
    if new_trees_per_year != st.session_state["new_trees"]:
        st.session_state["new_trees"] = new_trees_per_year

    if st.button("Calculate"):
        projected_data = project_tree_growth(data, years=20, new_trees_per_year=st.session_state["new_trees"])
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
            title="Projected Tree Growth Over Time"
        )
        st.plotly_chart(fig)

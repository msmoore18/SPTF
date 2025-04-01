import streamlit as st
import pandas as pd
import plotly.express as px
import msoffcrypto
import io

# Streamlit page configuration
st.set_page_config(layout="wide")

# Load password-protected Excel file
def load_data(password):
    file_path = "SPTF_Inventory_25.xlsx"
    try:
        with open(file_path, "rb") as file:
            decrypted = io.BytesIO()
            office_file = msoffcrypto.OfficeFile(file)

            if not office_file.is_encrypted():
                return pd.read_excel(file_path, sheet_name=None)

            office_file.load_key(password)
            office_file.decrypt(decrypted)
            return pd.read_excel(decrypted, sheet_name=None)
    except Exception:
        return None

# User enters password
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

    if "password_error" not in st.session_state:
        st.session_state["password_error"] = False

    st.text_input("Excel File Password:", type="password", key="password_input", on_change=submit_password)

    if st.button("Enter"):
        submit_password()

    if st.session_state.get("password_error"):
        st.error("Incorrect password or file issue. Please try again.")
    elif "data" in st.session_state:
        st.rerun()

    st.stop()

# Ensure data is available before proceeding
if "data" in st.session_state:
    sheets = st.session_state["data"]
    data = sheets["Inventory"]
    sales_data = sheets["Sales"]
else:
    st.stop()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go To", ["Inventory: Plots", "Inventory: Table", "Sales: Plots", "SPTF Lot Map"])

# Inventory Pages
if page in ["Inventory: Plots", "Inventory: Table"]:
    st.sidebar.header("Filter Options")
    height_range = st.sidebar.slider("Select Tree Height Range (ft)", float(data["Tree Height (ft)"].min()), float(data["Tree Height (ft)"].max()), (float(data["Tree Height (ft)"].min()), float(data["Tree Height (ft)"].max())), 0.5)

    quality_order = ["A", "B", "C", "OC"]
    available_qualities = [q for q in quality_order if q in data["Quality"].unique()]
    default_selection = [q for q in ["A", "B", "C"] if q in available_qualities]

    quality_options = st.sidebar.multiselect("Select Quality", options=available_qualities, default=default_selection)

    st.sidebar.markdown("**A** = Good  \n**B** = Needs Pruning  \n**C** = Needs to be Cut  \n**OC** = Overcrowded")

    lot_options = ['All'] + sorted(data["Lot"].unique(), key=lambda x: int(str(x)))
    selected_lot = st.sidebar.selectbox("Select Lot (see Lot Map)", options=lot_options)

    if selected_lot == 'All':
        lots = data["Lot"].unique()
    else:
        lots = [selected_lot]

    filtered_data = data[(data["Lot"].isin(lots)) & (data["Tree Height (ft)"].between(height_range[0], height_range[1])) & (data["Quality"].isin(quality_options))]

    if page == "Inventory: Plots":
        st.title("2025 Inventory for Spruce Point Tree Farm")
        st.markdown(f"<h3 style='color:green;'>Total Tree Count Based on Filter Selections: {filtered_data['Count'].sum()}</h3>", unsafe_allow_html=True)

        height_group = filtered_data.groupby("Tree Height (ft)")["Count"].sum()
        fig = px.bar(height_group.reset_index(), x='Tree Height (ft)', y='Count')
        st.plotly_chart(fig)

        height_bins = pd.cut(filtered_data["Tree Height (ft)"], bins=[0, 5, 10, 15, 20, float('inf')], labels=["0-5ft", "6-10ft", "11-15ft", "16-20ft", ">20ft"])
        height_distribution = filtered_data.groupby(height_bins)["Count"].sum().reset_index()
        fig = px.pie(height_distribution, names="Tree Height (ft)", values="Count")
        st.plotly_chart(fig)

        if selected_lot == 'All':
            fig_lot = px.bar(filtered_data.groupby("Lot")["Count"].sum().reset_index(), x='Lot', y='Count')
            st.plotly_chart(fig_lot)
        else:
            fig_lot = px.bar(filtered_data.groupby("Row")["Count"].sum().reset_index(), x='Row', y='Count')
            st.plotly_chart(fig_lot)

    elif page == "Inventory: Table":
        st.title("2025 Inventory for Spruce Point Tree Farm")
        st.markdown(f"<h3 style='color:green;'>Total Tree Count Based on Filter Selections: {filtered_data['Count'].sum()}</h3>", unsafe_allow_html=True)

        tree_summary = filtered_data.groupby(["Quality", "Lot", "Row", "Tree Height (ft)"])["Count"].sum().reset_index()
        tree_summary["Work Completed?"] = ""
        st.dataframe(tree_summary, hide_index=True)

elif page == "SPTF Lot Map":
    st.title("SPTF Lot Map")
    st.image("map_larger.png")

# Sales Plots
elif page == "Sales: Plots":
    st.title("Spruce Point Tree Farm Sales History")

    st.sidebar.header("Sales Filters")
    height_range = st.sidebar.slider("Tree Height Range (ft)", float(sales_data["Tree Height (ft)"].min()), float(sales_data["Tree Height (ft)"].max()), (float(sales_data["Tree Height (ft)"].min()), float(sales_data["Tree Height (ft)"].max())), 0.5)

    quality_options = st.sidebar.multiselect("Select Quality (A & B only)", ["A", "B"], default=["A", "B"])

    customer = sorted(sales_data["Customer"].dropna().unique())
    selected_customer = st.sidebar.selectbox("Select Customer", options=["All"] + list(customer))

    years = sorted(sales_data["Sales Year"].dropna().unique())
    selected_years = st.sidebar.multiselect("Select Sales Year(s)", years, default=years)

    metric = st.sidebar.radio("Select Metric", ["Tree Count", "Revenue"])

    sales_filtered = sales_data[(sales_data["Tree Height (ft)"].between(height_range[0], height_range[1])) & (sales_data["Quality"].isin(quality_options))]

    if selected_customer != "All":
        sales_filtered = sales_filtered[sales_filtered["Customer"] == selected_customer]

    if 'All' not in selected_years:
        sales_filtered = sales_filtered[sales_filtered["Sales Year"].isin(selected_years)]

    sales_filtered = sales_filtered.copy()
    sales_filtered["Revenue"] = sales_filtered["Quantity"] * sales_filtered["Cost Per Tree"]

    if metric == "Tree Count":
        st.markdown(f"<h3 style='color:green;'>Total Tree Sales Based on Filter Selections: {sales_filtered['Quantity'].sum()}</h3>", unsafe_allow_html=True)

        fig = px.bar(sales_filtered.groupby("Tree Height (ft)")["Quantity"].sum().reset_index(), x="Tree Height (ft)", y="Quantity", labels={"Quantity": "Tree Count"})
        st.plotly_chart(fig)

        fig = px.pie(sales_filtered.groupby("Customer")["Quantity"].sum().reset_index(), names="Customer", values="Quantity")
        st.plotly_chart(fig)

    elif metric == "Revenue":
        st.markdown(f"<h3 style='color:green;'>Total Revenue Based on Filter Selections: ${sales_filtered['Revenue'].sum():,.2f}</h3>", unsafe_allow_html=True)

        fig = px.bar(sales_filtered.groupby("Tree Height (ft)")["Revenue"].sum().reset_index(), x="Tree Height (ft)", y="Revenue", labels={"Revenue": "Revenue"})
        st.plotly_chart(fig)

        fig = px.pie(sales_filtered.groupby("Customer")["Revenue"].sum().reset_index(), names="Customer", values="Revenue")
        st.plotly_chart(fig)

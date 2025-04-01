import streamlit as st
import pandas as pd
import plotly.express as px
import msoffcrypto
import io

# --- Streamlit config ---
st.set_page_config(layout="wide")

# --- Load Excel data (Inventory + Sales) ---
def load_data(password):
    file_path = "SPTF_Inventory_25.xlsx"
    try:
        with open(file_path, "rb") as file:
            decrypted = io.BytesIO()
            office_file = msoffcrypto.OfficeFile(file)
            if not office_file.is_encrypted():
                excel = pd.ExcelFile(file_path)
            else:
                office_file.load_key(password)
                office_file.decrypt(decrypted)
                excel = pd.ExcelFile(decrypted)
            # Read both sheets
            inventory_data = pd.read_excel(excel, sheet_name="Inventory")
            sales_data = pd.read_excel(excel, sheet_name="Sales")

            # --- Clean & Standardize ---
            inventory_data.columns = inventory_data.columns.str.strip()
            sales_data.columns = sales_data.columns.str.strip()

            # Rename and extract year
            sales_data.rename(columns={"Transaction Date": "Sales Year"}, inplace=True)
            sales_data["Sales Year"] = pd.to_datetime(sales_data["Sales Year"], errors='coerce').dt.year
            sales_data.dropna(subset=["Sales Year"], inplace=True)
            sales_data["Sales Year"] = sales_data["Sales Year"].astype(int)
            
            return inventory_data, sales_data
    except Exception:
        return None, None

# --- First password for accessing data ---
if "inventory_data" not in st.session_state or "sales_data" not in st.session_state:
    st.title("Enter Password to Access Data")

    def submit_password():
        password = st.session_state.password_input
        if password:
            inventory_data, sales_data = load_data(password)
            if inventory_data is None:
                st.session_state["password_error"] = True
            else:
                st.session_state["inventory_data"] = inventory_data
                st.session_state["sales_data"] = sales_data
                st.session_state["password_error"] = False

    if "password_error" not in st.session_state:
        st.session_state["password_error"] = False

    st.text_input("Excel File Password:", type="password", key="password_input", on_change=submit_password)
    if st.button("Enter"):
        submit_password()
    if st.session_state.get("password_error"):
        st.error("Incorrect password or file issue. Please try again.")
    elif "inventory_data" in st.session_state and "sales_data" in st.session_state:
        st.rerun()
    st.stop()

# --- Loaded Data ---
inventory_data = st.session_state["inventory_data"]
sales_data = st.session_state["sales_data"]

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go To", ["Inventory: Plots", "Inventory: Table", "SPTF Lot Map", "Sales: Plots"])

# --- Inventory Pages ---
if page in ["Inventory: Plots", "Inventory: Table"]:
    st.sidebar.header("Filter Options")
    height_range = st.sidebar.slider("Select Tree Height Range (ft)",
        float(inventory_data["Tree Height (ft)"].min()),
        float(inventory_data["Tree Height (ft)"].max()),
        (float(inventory_data["Tree Height (ft)"].min()), float(inventory_data["Tree Height (ft)"].max())),
        0.5)

    quality_order = ["A", "B", "C", "OC"]
    available_qualities = [q for q in quality_order if q in inventory_data["Quality"].unique()]
    default_selection = [q for q in ["A", "B", "C"] if q in available_qualities]

    quality_options = st.sidebar.multiselect("Select Quality", available_qualities, default=default_selection)

    st.sidebar.markdown("**A** = Good  \n**B** = Needs Pruning  \n**C** = Needs to be Cut  \n**OC** = Overcrowded")

    lot_options = ['All'] + sorted(inventory_data["Lot"].unique(), key=lambda x: int(str(x)))
    selected_lot = st.sidebar.selectbox("Select Lot (see Lot Map)", options=lot_options)

    if selected_lot == 'All':
        lots = inventory_data["Lot"].unique()
    else:
        lots = [selected_lot]

    filtered_data = inventory_data[(inventory_data["Lot"].isin(lots)) &
        (inventory_data["Tree Height (ft)"].between(height_range[0], height_range[1])) &
        (inventory_data["Quality"].isin(quality_options))]

    if page == "Inventory: Plots":
        st.title("2025 Inventory for Spruce Point Tree Farm")
        st.markdown(f"<h3 style='color:green;'>Total Tree Count: {filtered_data['Count'].sum()}</h3>", unsafe_allow_html=True)
        fig = px.bar(filtered_data.groupby("Tree Height (ft)")["Count"].sum().reset_index(), x="Tree Height (ft)", y="Count")
        st.plotly_chart(fig)
        height_bins = pd.cut(filtered_data["Tree Height (ft)"], bins=[0,5,10,15,20,float('inf')], labels=["0-5ft","6-10ft","11-15ft","16-20ft",">20ft"])
        fig = px.pie(filtered_data.groupby(height_bins)["Count"].sum().reset_index(), names="Tree Height (ft)", values="Count")
        st.plotly_chart(fig)

        if selected_lot == 'All':
            fig = px.bar(filtered_data.groupby("Lot")["Count"].sum().reset_index(), x="Lot", y="Count")
            st.plotly_chart(fig)
        else:
            fig = px.bar(filtered_data.groupby("Row")["Count"].sum().reset_index(), x="Row", y="Count")
            st.plotly_chart(fig)

    elif page == "Inventory: Table":
        st.title("2025 Inventory Table")
        st.markdown(f"<h3 style='color:green;'>Total Tree Count: {filtered_data['Count'].sum()}</h3>", unsafe_allow_html=True)
        tree_summary = filtered_data.groupby(["Quality", "Lot", "Row", "Tree Height (ft)"])["Count"].sum().reset_index()
        tree_summary["Work Completed?"] = ""
        st.dataframe(tree_summary, hide_index=True)

elif page == "SPTF Lot Map":
    st.title("SPTF Lot Map")
    st.image("map_larger.png")

# --- Sales Page (Password Protected) ---
elif page == "Sales: Plots":
    if "sales_access" not in st.session_state:
        st.title("Sales Data Access")
        sales_pw = st.text_input("Enter Sales Password:", type="password")
        if st.button("Unlock Sales Page"):
            if sales_pw == "sptf!":
                st.session_state["sales_access"] = True
                st.rerun()
            else:
                st.error("Incorrect Sales Password")
        st.stop()
    else:
        st.title("Sales: Plots")

        st.sidebar.header("Sales Filters")
        height_range = st.sidebar.slider("Tree Height Range (ft)",
            float(sales_data["Tree Height (ft)"].min()),
            float(sales_data["Tree Height (ft)"].max()),
            (float(sales_data["Tree Height (ft)"].min()), float(sales_data["Tree Height (ft)"].max())),
            0.5)

        quality_options = st.sidebar.multiselect("Select Quality (A & B only)", ["A", "B"], default=["A", "B"])

        customers = sorted(sales_data["Customer"].dropna().unique())
        selected_customer = st.sidebar.multiselect("Select Customer(s)", customers, default=customers)

        years = sorted(sales_data["Sales Year"].dropna().unique())
        selected_years = st.sidebar.multiselect("Select Sales Year(s)", years, default=years)

        sales_filtered = sales_data[(sales_data["Tree Height (ft)"].between(height_range[0], height_range[1])) &
            (sales_data["Quality"].isin(quality_options))]

        if selected_customer:
            sales_filtered = sales_filtered[sales_filtered["Customer"].isin(selected_customer)]

        if selected_years:
            sales_filtered = sales_filtered[sales_filtered["Sales Year"].isin(selected_years)]

        st.subheader("Trees Sold vs Tree Height")
        fig = px.bar(sales_filtered.groupby("Tree Height (ft)")["Quantity"].sum().reset_index(), x="Tree Height (ft)", y="Quantity")
        st.plotly_chart(fig)

        st.subheader("Trees Sold by Customer")
        fig = px.pie(sales_filtered.groupby("Customer")["Quantity"].sum().reset_index(), names="Customer", values="Quantity")
        st.plotly_chart(fig)

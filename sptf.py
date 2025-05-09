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
page = st.sidebar.radio("Go To", ["Current Inventory", "Historical Sales", "Planting History", "Lot Map"])

# Page logic
if page == "Current Inventory":
    st.sidebar.header("Filter Options")
    height_range = st.sidebar.slider(
        "Select Tree Height Range (ft)",
        float(data["Tree Height (ft)"].min()),
        float(data["Tree Height (ft)"].max()),
        (float(data["Tree Height (ft)"].min()), float(data["Tree Height (ft)"].max())),
        0.5,
        key="inventory_height_slider_unique"
    )

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

    st.title("Current Tree Inventory")
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

    tree_summary = filtered_data.groupby(["Quality", "Lot", "Row", "Tree Height (ft)"])["Count"].sum().reset_index()
    tree_summary["Work Completed?"] = ""
    st.dataframe(tree_summary, hide_index=True)

elif page == "Lot Map":
    st.title("Lot Map")
    st.image("map_larger.png")

elif page == "Historical Sales":
    st.title("Historical Sales")

    st.sidebar.header("Sales Filters")
    years = sorted(sales_data["Sales Year"].dropna().unique())
    default_years = years[-2:] if len(years) >= 2 else years
    selected_years = st.sidebar.multiselect("Select Sales Year(s)", years, default=default_years)

    height_range = st.sidebar.slider(
        "Tree Height Range (ft)",
        float(sales_data["Tree Height (ft)"].min()),
        float(sales_data["Tree Height (ft)"].max()),
        (float(sales_data["Tree Height (ft)"].min()), float(sales_data["Tree Height (ft)"].max())),
        0.5,
        key="sales_height_slider_unique"
    )

    any_pre_2023 = any(yr < 2023 for yr in selected_years)
    st.sidebar.markdown("(The following filters are only available for years 2023 and beyond)")

    quality_options = ["A", "B"]
    selected_quality = quality_options
    if any_pre_2023:
        st.sidebar.multiselect("Select Quality (A & B only)", options=quality_options, default=quality_options, disabled=True)
    else:
        selected_quality = st.sidebar.multiselect("Select Quality (A & B only)", options=quality_options, default=quality_options)

    customer = sorted(sales_data["Customer"].dropna().unique())
    selected_customer = "All"
    if any_pre_2023:
        st.sidebar.selectbox("Select Customer", options=["All"], index=0, disabled=True)
    else:
        selected_customer = st.sidebar.selectbox("Select Customer", options=["All"] + list(customer))

    metric_options = ["Tree Count"] if any_pre_2023 else ["Tree Count", "Revenue"]
    metric = st.sidebar.radio("Select Metric", metric_options, index=0)

    sales_filtered = sales_data[(sales_data["Sales Year"].isin(selected_years)) & (sales_data["Tree Height (ft)"].between(height_range[0], height_range[1]))]
    if not any_pre_2023:
        sales_filtered = sales_filtered[sales_filtered["Quality"].isin(selected_quality)]
    if selected_customer != "All":
        sales_filtered = sales_filtered[sales_filtered["Customer"] == selected_customer]

    sales_filtered = sales_filtered.copy()
    sales_filtered["Revenue"] = sales_filtered["Quantity"] * sales_filtered["Cost Per Tree"]

    if metric == "Tree Count":
        st.markdown(f"<h3 style='color:green;'>Total Tree Sales Based on Filter Selections: {sales_filtered['Quantity'].sum()}</h3>", unsafe_allow_html=True)
        
        grouped = sales_filtered.groupby(["Tree Height (ft)", "Sales Year"])["Quantity"].sum().reset_index()
        grouped["Sales Year"] = grouped["Sales Year"].astype(str)
        fig_year_grouped = px.bar(grouped, x="Tree Height (ft)", y="Quantity", color="Sales Year", labels={"Quantity": "Tree Count"}, title="Tree Sales by Height and Year")
        fig_year_grouped.update_layout(barmode="stack")
        fig_year_grouped.update_layout(barmode="stack")
        st.plotly_chart(fig_year_grouped)

        if not any_pre_2023:
            if selected_customer == "All":
                fig = px.pie(
                    sales_filtered.groupby("Customer")["Quantity"].sum().reset_index(),
                    names="Customer",
                    values="Quantity",
                    title="Tree Sales Distribution by Customer"
                )
            else:
                fig = px.pie(
                    sales_filtered.groupby("Tree Height (ft)")["Quantity"].sum().reset_index(),
                    names="Tree Height (ft)",
                    values="Quantity",
                    title=f"{selected_customer} - Tree Sales Distribution by Height"
                )
            st.plotly_chart(fig)
    else:
        st.markdown(f"<h3 style='color:green;'>Total Revenue Based on Filter Selections: ${sales_filtered['Revenue'].sum():,.2f}</h3>", unsafe_allow_html=True)
        
        grouped = sales_filtered.groupby(["Tree Height (ft)", "Sales Year"])["Revenue"].sum().reset_index()
        grouped["Sales Year"] = grouped["Sales Year"].astype(str)
        fig_year_grouped = px.bar(grouped, x="Tree Height (ft)", y="Revenue", color="Sales Year", labels={"Revenue": "Revenue ($)"}, title="Revenue by Height and Year")
        fig_year_grouped.update_layout(barmode="stack")
        fig_year_grouped.update_yaxes(tickprefix="$")
        st.plotly_chart(fig_year_grouped)

        if not any_pre_2023:
            fig = px.pie(
                sales_filtered.groupby("Customer")["Revenue"].sum().reset_index(),
                names="Customer",
                values="Revenue",
                title="Revenue Distribution by Customer"
            )
            fig.update_traces(textinfo='percent+value', texttemplate='%{percent} <br> $%{value:,.0f}')
            st.plotly_chart(fig)

elif page == "Planting History":
    if "data" not in st.session_state:
        st.warning("Please enter the password on the home page to unlock the data.")
        st.stop()
    sheets = st.session_state["data"]
    st.title("Planting History")
    

    planting_data = sheets["Planting"].copy()
    planting_data["Date"] = pd.to_datetime(planting_data["Date"])
    planting_data["Year"] = planting_data["Date"].dt.year

    id_columns = ["Date", "Year", "Lot #", "Row #"]
    height_columns = [col for col in planting_data.columns if col not in id_columns and str(col).strip().isdigit()]

    long_df = planting_data.melt(
        id_vars=id_columns,
        value_vars=height_columns,
        var_name="Tree Height (in)",
        value_name="Count"
    )

    long_df["Tree Height (in)"] = pd.to_numeric(long_df["Tree Height (in)"], errors="coerce")
    long_df = long_df.dropna(subset=["Tree Height (in)", "Count"])
    long_df["Count"] = long_df["Count"].astype(int)

    st.sidebar.header("Planting Filters")
    min_height_val = long_df["Tree Height (in)"].dropna().min()
    min_height = int(min_height_val) if pd.notnull(min_height_val) else 0
    max_height_val = long_df["Tree Height (in)"].dropna().max()
    max_height = int(max_height_val) if pd.notnull(max_height_val) else 100
    height_range = st.sidebar.slider("Tree Height Range (in)", min_height, max_height, (min_height, max_height), step=6, key="planting_height_slider_unique")

    lot_options = ["All"] + sorted(long_df["Lot #"].dropna().unique(), key=lambda x: int(str(x)))
    selected_lot = st.sidebar.selectbox("Select Lot", lot_options)

    filtered = long_df[long_df["Tree Height (in)"].between(height_range[0], height_range[1])]
    if selected_lot != "All":
        filtered = filtered[filtered["Lot #"] == selected_lot]

    st.markdown(f"<h3 style='color:green;'>Total Tree Planting Count Based on Filter Selections: {filtered['Count'].sum()}</h3>", unsafe_allow_html=True)

    grouped = filtered.groupby(["Tree Height (in)", "Year"])["Count"].sum().reset_index()
    grouped["Year"] = grouped["Year"].astype(str)
    grouped["Year"] = grouped["Year"].astype(str)
    fig1 = px.bar(grouped, x="Tree Height (in)", y="Count", color="Year", color_discrete_sequence=px.colors.qualitative.Safe, title="Trees Planted by Height and Year", labels={"Count": "Trees Planted"})
    fig1.update_layout(barmode="stack")
    fig1.update_traces(marker_line_width=0)
    fig1.update_layout(legend_title_text="Year")
    st.plotly_chart(fig1)

    pie_data = filtered.groupby("Tree Height (in)")["Count"].sum().reset_index()
    fig2 = px.pie(pie_data, names="Tree Height (in)", values="Count", title="Distribution of Trees by Height (in)")
    st.plotly_chart(fig2)

    if selected_lot == "All":
        lot_group = filtered.groupby(["Lot #", "Year"])["Count"].sum().reset_index()
        lot_group["Year"] = lot_group["Year"].astype(str)
        fig3 = px.bar(lot_group, x="Lot #", y="Count", color="Year", title="Trees Planted by Lot", labels={"Count": "Trees Planted"})
        fig3.update_layout(barmode="stack")
    else:
        row_group = filtered.groupby("Row #")["Count"].sum().reset_index()
        fig3 = px.bar(row_group, x="Row #", y="Count", title=f"Trees Planted by Row in Lot {selected_lot}", labels={"Count": "Trees Planted"})
    st.plotly_chart(fig3)

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
                return pd.read_excel(file_path)

            office_file.load_key(password)
            office_file.decrypt(decrypted)
            return pd.read_excel(decrypted)
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

    # Initialize the error state
    if "password_error" not in st.session_state:
        st.session_state["password_error"] = False

    st.text_input(
        "Excel File Password:",
        type="password",
        key="password_input",
        on_change=submit_password
    )

    if st.button("Enter"):
        submit_password()

    # Handle errors or success after callback/button press
    if st.session_state.get("password_error"):
        st.error("Incorrect password or file issue. Please try again.")
    elif "data" in st.session_state:
        st.rerun()  # Now outside the callback, safe to call

    st.stop()

# Ensure data is available before proceeding
if "data" in st.session_state:
    data = st.session_state["data"]
else:
    st.stop()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Lot Map", "Tree Inventory", "Tree Maintenance"])

# Show filter options only if not on the "Lot Map" page
if page != "Lot Map":
    st.sidebar.header("Filter Options")
    height_range = st.sidebar.slider(
        "Select Tree Height Range (ft)",
        float(data["Tree Height (ft)"].min()),
        float(data["Tree Height (ft)"].max()),
        (
            float(data["Tree Height (ft)"].min()), 
            float(data["Tree Height (ft)"].max())
        ),
        0.5
    )

    # Ensure "OC" is included in the quality filter
    quality_options = st.sidebar.multiselect(
        "Select Quality",
        options=data["Quality"].unique(),
        default=[q for q in data["Quality"].unique() if q in ["A", "B", "C", "OC"]]
    )
    st.sidebar.write("A = Good")
    st.sidebar.write("B = Needs Pruning")
    st.sidebar.write("C = Needs to be Cut")
    st.sidebar.write("OC = Overcrowded")

    lot_options = ['All'] + sorted(data["Lot"].unique(), key=lambda x: int(str(x)))
    selected_lot = st.sidebar.selectbox("Select Lot", options=lot_options)
    if selected_lot == 'All':
        lots = data["Lot"].unique()
    else:
        lots = [selected_lot]

    # Filter data based on selections
    filtered_data = data[
        (data["Lot"].isin(lots)) & 
        (data["Tree Height (ft)"].between(height_range[0], height_range[1])) & 
        (data["Quality"].isin(quality_options))
    ]

if page == "Tree Inventory":
    st.title("2025 Inventory for Spruce Point Tree Farm")
    st.markdown(f"<h3 style='color:green;'>Total Tree Count Based on Filter Selections: {filtered_data['Count'].sum()}</h3>", unsafe_allow_html=True)

    # Tree Count vs Tree Height
    height_group = filtered_data.groupby("Tree Height (ft)")["Count"].sum()
    fig = px.bar(height_group.reset_index(), x='Tree Height (ft)', y='Count', 
                 labels={'Tree Height (ft)': 'Tree Height (ft)', 'Count': 'Tree Count'})
    fig.update_layout(xaxis=dict(tickmode='array', tickvals=height_group.index))
    st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
    st.plotly_chart(fig)
    st.markdown('</div>', unsafe_allow_html=True)

    # Pie Chart
    height_bins = pd.cut(filtered_data["Tree Height (ft)"], bins=[0, 5, 10, 15, 20, float('inf')], 
                         labels=["0-5ft", "6-10ft", "11-15ft", "16-20ft", ">20ft"])
    height_distribution = filtered_data.groupby(height_bins)["Count"].sum().reset_index()
    fig = px.pie(height_distribution, names="Tree Height (ft)", values="Count")
    fig.update_layout(legend=dict(x=.1, y=0.5))
    st.plotly_chart(fig)

    # Tree Count vs Lot (only appears if selected_lot == 'All')
    if selected_lot == 'All':
        lot_group = filtered_data.groupby("Lot")["Count"].sum().reset_index()
        fig_lot = px.bar(lot_group, x='Lot', y='Count',
                         labels={'Lot': 'Lot', 'Count': 'Tree Count'})
        fig_lot.update_layout(xaxis=dict(type='category'))
    
        st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
        st.plotly_chart(fig_lot)
        st.markdown('</div>', unsafe_allow_html=True)

    # Tree Count vs Row (only appears if selected_lot does not = 'All')
    if selected_lot != 'All':
        lot_group = filtered_data.groupby("Row")["Count"].sum().reset_index()
        fig_lot = px.bar(lot_group, x='Row', y='Count',
                         labels={'Row': 'Row', 'Count': 'Tree Count'})
        fig_lot.update_layout(xaxis=dict(type='category'))
    
        st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
        st.plotly_chart(fig_lot)
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "Lot Map":
    st.title("Lot Map")
    st.image("map_larger.png")

elif page == "Tree Maintenance":
    st.title("Tree Maintenance Table")
    st.markdown(f"<h3 style='color:green;'>Total Tree Count Based on Filter Selections: {filtered_data['Count'].sum()}</h3>", unsafe_allow_html=True)

    # Filtered summary of trees
    tree_summary = filtered_data.groupby(["Quality", "Lot", "Row", "Tree Height (ft)"])['Count'].sum().reset_index()
    tree_summary["Work Completed?"] = ""

    # Display table
    csv = tree_summary.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Table as CSV",
        data=csv,
        file_name="tree_summary.csv",
        mime="text/csv"
    )
    st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
    st.dataframe(tree_summary, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)


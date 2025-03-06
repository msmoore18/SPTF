import streamlit as st
import pandas as pd
import plotly.express as px
import msoffcrypto
import io

# Streamlit page configuration
st.set_page_config(layout="wide")

# Load data from a password-protected Excel file
@st.cache_data
def load_data(password=None):
    file_path = "SPTF_Count.xlsx"

    try:
        with open(file_path, "rb") as file:
            decrypted = io.BytesIO()
            office_file = msoffcrypto.OfficeFile(file)
            office_file.load_key(password)  # Load the provided password
            office_file.decrypt(decrypted)
            return pd.read_excel(decrypted)  # Read decrypted Excel file
    except Exception:
        return None  # Return None if password is incorrect or file is not encrypted

# User inputs password
password = st.sidebar.text_input("Enter Excel Password", type="password")

if password:
    data = load_data(password)
    if data is None:
        st.error("Incorrect password or file issue. Please try again.")
        st.stop()
else:
    st.warning("Please enter a password to load the Excel file.")
    st.stop()


# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Lot Map", "Tree Inventory", "Projected Tree Inventory", "Tree Maintenance"])

# Sidebar filters
st.sidebar.header("Filter Options")
height_range = st.sidebar.slider(
    "Select Tree Height Range (ft)",
    int(data["Tree Height (ft)"].min()),
    int(data["Tree Height (ft)"].max()),
    (
        int(data["Tree Height (ft)"].min()),
        int(data["Tree Height (ft)"].max())
    )
)

quality_options = st.sidebar.multiselect(
    "Select Quality",
    options=data["Quality"].unique(),
    default=data["Quality"].unique()
)

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
  
    st.write(f"### Total Tree Count Based on Filter Selections: {filtered_data['Count'].sum()}")
    
    col1, col2 = st.columns([4, 2])
    with col1:
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
        fig.update_layout(legend=dict(x=-0.4, y=0.5))
        st.plotly_chart(fig)

elif page == "Lot Map":
    st.title("Lot Map")
    st.image("SPTF.png", width=300)



elif page == "Projected Tree Inventory":
    st.title("Under Construction")

elif page == "Tree Maintenance":
    st.title("Tree Maintenance Table")
    st.write(f"### Total Tree Count Based on Filter Selections: {filtered_data['Count'].sum()}")
    st.write("This page lets you customize and download a printable table for Rudy. Use the filters on the left to select which Quality (B: Needs Pruning, C: Needs to be cut), Lot #, and Tree Height you want displayed in the table")
    
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

  

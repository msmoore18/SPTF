import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Reduce side margins
st.set_page_config(layout="wide")

# Load data from Excel file in the same GitHub repository
@st.cache_data
def load_data():
    return pd.read_excel("SPTF_Count.xlsx")  # Ensure 'SPTF_Tree_Count.xlsx' is in the same repo

data = load_data()


# Sidebar for navigation
st.sidebar.markdown("# Navigation")
page = st.sidebar.radio("# Go to", ["Tree Inventory", "Tree Maintenance", "SPTF Lot Map"])

# Sidebar for filters
st.sidebar.header("Filter Options")

# Tree Height filter
height_range = st.sidebar.slider(
    "Select Tree Height Range (ft)",
    int(data["Tree Height (ft)"].min()),
    int(data["Tree Height (ft)"].max()),
    (
        int(data["Tree Height (ft)"].min()),
        int(data["Tree Height (ft)"].max())
    )
)

# Quality filter
quality_options = st.sidebar.multiselect(
    "Select Quality",
    options=data["Quality"].unique(),
    default=data["Quality"].unique()
)
if page == "Tree Maintenance":
    lot_options = ['All'] + sorted(data["Lot"].unique(), key=lambda x: int(str(x)))
    selected_lot = st.sidebar.selectbox("Select Lot", options=lot_options)
    if selected_lot == 'All':
        lots = data["Lot"].unique()
    else:
        lots = [selected_lot]
if page == "Tree Inventory":
    st.title("2025 Inventory for Spruce Point Tree Farm")
    
    lot_options = ['All'] + sorted(data["Lot"].unique(), key=lambda x: int(str(x)))
    selected_lot = st.sidebar.selectbox("Select Lot", options=lot_options)
    if selected_lot == 'All':
        lots = data["Lot"].unique()
    else:
        lots = [selected_lot]

# Filter data based on selected filters
filtered_data = data[
    (data["Lot"].isin([lots]) if isinstance(lots, int) else data["Lot"].isin(lots)) &
    (data["Tree Height (ft)"].between(height_range[0], height_range[1])) &
    (data["Quality"].isin(quality_options))
]

if page == "Tree Inventory":
    # Layout: Main content on left, image on right
    col1, col2 = st.columns([4, 2])

    with col1:
        # Bar Chart: Tree Count vs Tree Height
        height_group = filtered_data.groupby("Tree Height (ft)")["Count"].sum()
        
        fig = px.bar(height_group.reset_index(), x='Tree Height (ft)', y='Count', hover_data={'Tree Height (ft)': True, 'Count': True}, category_orders={'Tree Height (ft)': sorted(data['Tree Height (ft)'].unique())}, labels={'Tree Height (ft)': 'Tree Height (ft)', 'Count': 'Tree Count'})
        fig.update_layout(xaxis=dict(tickmode='array', tickvals=height_group.index))
        st.plotly_chart(fig, use_container_width=True)
        
        # Pie Chart: Tree Count by Height Range
        height_bins = pd.cut(filtered_data["Tree Height (ft)"], bins=[0, 5, 10, 15, 20, float('inf')], labels=["0-5ft", "6-10ft", "11-15ft", "16-20ft", ">20ft"])
        height_distribution = filtered_data.groupby(height_bins)["Count"].sum().reset_index()
        fig = px.pie(height_distribution, names="Tree Height (ft)", values="Count", width=600, height=600)
        fig.update_layout(legend=dict(x=-0.4, y=0.5))
        fig.update_traces(textinfo='percent', insidetextorientation='horizontal')
        st.plotly_chart(fig)

    

elif page == "Tree Maintenance":
    st.title("Tree Maintenance Table")
    st.write("Use this page to download a printable table for Rudy. Use the filters on the left to select which Quality (B: Needs Pruning, C: Needs to be cut), Lot #, and Tree Height you want displayed in the table")

elif page == "SPTF Lot Map":
    st.title("SPTF Lot Map")
    st.image("SPTF.png", width=600)
    st.title("Tree Maintenance Table")
    st.write("Use this page to download a printable table for Rudy. Use the filters on the left to select which Quality (B: Needs Pruning, C: Needs to be cut), Lot #, and Tree Height you want displayed in the table")
    
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
    st.dataframe(tree_summary, hide_index=True)
    
    

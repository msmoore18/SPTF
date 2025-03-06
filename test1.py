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
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Bob's Page", "Rudy's Page"])

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
if page == "Rudy's Page":
    lots = st.sidebar.selectbox("Select Lot", options=data["Lot"].unique())
else:
    lots = st.sidebar.multiselect("Select Lots", options=data["Lot"].unique(), default=data["Lot"].unique())

# Filter data based on selected filters
filtered_data = data[
    (data["Lot"].isin([lots]) if isinstance(lots, int) else data["Lot"].isin(lots)) &
    (data["Tree Height (ft)"].between(height_range[0], height_range[1])) &
    (data["Quality"].isin(quality_options))
]

if page == "Bob's Page":
    # Layout: Main content on left, image on right
    col1, col2 = st.columns([4, 2])

    with col1:
        # Bar Chart: Tree Count vs Tree Height
        st.write("### Tree Count vs Tree Height")
        height_group = filtered_data.groupby("Tree Height (ft)")["Count"].sum()
        
        fig = px.bar(height_group.reset_index(), x='Tree Height (ft)', y='Count', hover_data={'Tree Height (ft)': True, 'Count': True}, category_orders={'Tree Height (ft)': sorted(data['Tree Height (ft)'].unique())}, labels={'Tree Height (ft)': 'Tree Height (ft)', 'Count': 'Tree Count'})
        fig.update_layout(xaxis=dict(tickmode='array', tickvals=height_group.index))
        st.plotly_chart(fig)

        # Pie Chart: Tree Count by Height Range
        st.write("### Tree Count vs Height")
        height_bins = pd.cut(filtered_data["Tree Height (ft)"], bins=[0, 5, 10, 15, 20, float('inf')], labels=["0-5ft", "6-10ft", "11-15ft", "16-20ft", ">20ft"])
        height_distribution = filtered_data.groupby(height_bins)["Count"].sum().reset_index()
        fig = px.pie(height_distribution, names="Tree Height (ft)", values="Count")
        st.plotly_chart(fig)

    with col2:
        # Display Image
        st.image("SPTF.png", width=375)

elif page == "Rudy's Page":
    
    # B Trees Table: To Be Pruned
    st.write("### B Trees: To Be Pruned")
    b_trees = data[data['Quality'] == 'B'][['Lot', 'Row', 'Tree Height (ft)', 'Count']]
    if not b_trees.empty:
        st.dataframe(b_trees, hide_index=True)
    else:
        st.write("No B quality trees found.")
    
    # C Trees Table: To Be Cut
    st.write("### C Trees: To Be Cut")
    c_trees = data[data['Quality'] == 'C'][['Lot', 'Row', 'Tree Height (ft)']]
    if not c_trees.empty:
        st.dataframe(c_trees, hide_index=True)
    else:
        st.write("No C quality trees found.")
  

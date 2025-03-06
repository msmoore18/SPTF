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
    lots = st.sidebar.radio("Select Lot", options=data["Lot"].unique())

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
    
    # Layout: Main content on left, image on right
    col1, col2 = st.columns([4, 2])

    with col1:
        # Bar Chart: Tree Count vs Row (Stacked by Quality)
        st.write(f"### Lot {lots} Tree Count")
        row_group = filtered_data.groupby(["Row", "Quality"])["Count"].sum().reset_index()
        fig = px.bar(row_group, x='Row', y='Count', color='Quality', barmode='stack', labels={'Row': 'Row', 'Count': 'Tree Count', 'Quality': 'Quality'}, hover_data={'Row': True, 'Count': True, 'Quality': True})
        fig.update_layout(xaxis=dict(tickmode='linear'))
        st.plotly_chart(fig)
    
    with col2:
        # Display Image
        st.image("SPTF.png", width=375)

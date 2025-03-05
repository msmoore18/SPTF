import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Reduce side margins
st.set_page_config(layout="wide")

# Load data from Excel file in the same GitHub repository
@st.cache_data
def load_data():
    return pd.read_excel("SPTF_Tree_Count.xlsx")  # Ensure 'SPTF_Tree_Count.xlsx' is in the same repo

data = load_data()

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
lots = st.sidebar.multiselect("Select Lots", options=data["Lot"].unique(), default=data["Lot"].unique())

# Filter data based on selected filters
filtered_data = data[
    (data["Lot"].isin(lots)) &
    (data["Tree Height (ft)"].between(height_range[0], height_range[1])) &
    (data["Quality"].isin(quality_options))
]

# Layout: Main content on left, image on right
col1, col2 = st.columns([4, 2])

with col1:
    # Bar Chart: Tree Count vs Tree Height
    st.write("### Tree Count vs Tree Height")
    height_group = filtered_data.groupby(["Tree Height (ft)", "Quality"])["Count"].sum().reset_index()
    fig = px.bar(height_group, x='Tree Height (ft)', y='Count', color='Quality', barmode='stack', 
                 labels={'Tree Height (ft)': 'Tree Height (ft)', 'Count': 'Tree Count'}, 
                 hover_data={'Tree Height (ft)': True, 'Count': True})
    st.plotly_chart(fig)

        # Bar Chart: Tree Count vs Row (only if one lot is selected)
    if len(lots) == 1:
        st.write("### Tree Count vs Row")
        row_group = filtered_data.groupby("Row")["Count"].sum()
        fig = px.bar(row_group.reset_index(), x='Row', y='Count', labels={'Row': 'Row', 'Count': 'Tree Count'}, hover_data={'Row': True, 'Count': True})
        fig.update_layout(xaxis=dict(tickmode='linear'))
        st.plotly_chart(fig)

with col2:
    # Display Image
    st.image("SPTF.png", width=375)

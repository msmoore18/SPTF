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
    height_group = filtered_data.groupby("Tree Height (ft)")["Count"].sum()
    
    fig = px.bar(height_group.reset_index(), x='Tree Height (ft)', y='Count', hover_data={'Tree Height (ft)': True, 'Count': True}, category_orders={'Tree Height (ft)': sorted(data['Tree Height (ft)'].unique())}, labels={'Tree Height (ft)': 'Tree Height (ft)', 'Count': 'Tree Count'})
    fig.update_layout(xaxis=dict(tickmode='array', tickvals=height_group.index))
    st.plotly_chart(fig)

        # Bar Chart: Tree Count vs Row (only if one lot is selected)
    if len(lots) == 1:
        st.write("### Tree Count vs Row")
        row_group = filtered_data.groupby(["Row", "Quality"])["Count"].sum().reset_index()
        fig = px.bar(row_group, x='Row', y='Count', color='Quality', barmode='stack', labels={'Row': 'Row', 'Count': 'Tree Count', 'Quality': 'Quality'}, hover_data={'Row': True, 'Count': True, 'Quality': True})
        fig.update_layout(xaxis=dict(tickmode='linear'))
        st.plotly_chart(fig)

with col1:
    # Pie Chart: Tree Count by Height Range
    st.write("### Tree Count vs Height")
    height_bins = pd.cut(filtered_data["Tree Height (ft)"], bins=[0, 5, 10, 15, 20, float('inf')], labels=["0-5ft", "6-10ft", "11-15ft", "16-20ft", ">20ft"])
    height_distribution = filtered_data.groupby(height_bins)["Count"].sum().reset_index()
    fig = px.pie(height_distribution, names="Tree Height (ft)", values="Count")
    st.plotly_chart(fig)

st.write("### Modify Tree Count")
selected_lot = st.selectbox("Select Lot", options=data["Lot"].unique())
selected_row = st.selectbox("Select Row", options=data[data["Lot"] == selected_lot]["Row"].unique())
selected_quality = st.selectbox("Select Quality", options=data["Quality"].unique())
selected_height = st.number_input("Tree Height (ft)", min_value=1, step=1)
new_count = st.number_input("New Tree Count", min_value=0, step=1)
x_position = st.number_input("X Position", step=1.0)
y_position = st.number_input("Y Position", step=1.0)

if st.button("Update Tree Count"):
    data.loc[(data["Lot"] == selected_lot) & (data["Row"] == selected_row) & (data["Quality"] == selected_quality) & (data["Tree Height (ft)"] == selected_height), ["Count", "X Position", "Y Position"]] = [new_count, x_position, y_position]
    data.to_excel("SPTF_Tree_Count.xlsx", index=False)
    st.success("Tree count updated successfully!")
    st.dataframe(data)  # Display updated data

with col2:
    # Display Image
    st.image("SPTF.png", width=375)
  

import streamlit as st
import pandas as pd
import plotly.express as px

# File uploader
st.sidebar.header("Upload Excel File")
uploaded_file = st.sidebar.file_uploader("Upload your tree farm data", type=["xlsx"])

if uploaded_file:
    data = pd.read_excel(uploaded_file)
    
    # Sidebar filters
    st.sidebar.header("Filters")
    locations = st.sidebar.multiselect("Select Locations", options=data["Location"].unique(), default=data["Location"].unique())
    quality = st.sidebar.multiselect("Select Quality", options=data["Quality"].unique(), default=data["Quality"].unique())
    height_range = st.sidebar.slider("Select Height Range", int(data["Height"].min()), int(data["Height"].max()), (int(data["Height"].min()), int(data["Height"].max())))

    # Apply filters
    filtered_data = data[(data["Location"].isin(locations)) & (data["Quality"].isin(quality)) & (data["Height"].between(height_range[0], height_range[1]))]

    # Display filtered data
    st.write("### Filtered Tree Data")
    st.dataframe(filtered_data)

    # Bar Chart: Number of Trees by Location
    st.write("### Number of Trees by Location")
    fig = px.bar(filtered_data["Location"].value_counts().reset_index(), x="index", y="Location", labels={"index": "Location", "Location": "Number of Trees"})
    st.plotly_chart(fig)

    # Bar Chart: Number of Trees by Quality
    st.write("### Number of Trees by Quality")
    fig = px.bar(filtered_data["Quality"].value_counts().reset_index(), x="index", y="Quality", labels={"index": "Quality", "Quality": "Number of Trees"})
    st.plotly_chart(fig)

    # Histogram: Tree Height Distribution
    st.write("### Tree Height Distribution")
    fig = px.histogram(filtered_data, x="Height", nbins=10, labels={"Height": "Tree Height"})
    st.plotly_chart(fig)

    st.write("### Summary Statistics")
    st.write(filtered_data.describe())
else:
    st.write("### Please upload an Excel file to proceed.")

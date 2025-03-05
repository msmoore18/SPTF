import streamlit as st
import pandas as pd
import plotly.express as px

# Sample data
data = pd.DataFrame({
    "Lot": [1, 1, 1, 2, 2],
    "Height": [12, 24, 12, 24, 24],
    "Quality": ["A", "A", "A", "B", "A"]
})

# Display data
st.write("### Tree Data")
st.dataframe(data)

# Bar Chart: Tree Height
st.write("### Tree Height by Lot")
fig = px.bar(data, x="Lot", y="Height", labels={"Lot": "Lot Number", "Height": "Tree Height"})
st.plotly_chart(fig)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data from Excel file in the same GitHub repository
@st.cache_data
def load_data():
    return pd.read_excel("SPTF_Tree_Count.xlsx")  # Ensure 'data.xlsx' is in the same repo

data = load_data()

# Sidebar for lot selection
st.sidebar.header("Filter Options")
lots = st.sidebar.multiselect("Select Lots", options=data["Lot"].unique(), default=data["Lot"].unique())

# Filter data based on selected lots
filtered_data = data[data["Lot"].isin(lots)]

# Layout: Main content on left, image on right
col1, col2 = st.columns([3, 1])

with col1:
    # Bar Chart: Tree Count vs Tree Height
    st.write("### Tree Count vs Tree Height")
    fig, ax = plt.subplots()
    height_group = filtered_data.groupby("Tree Height (ft)")["Count"].sum()
    height_group.plot(kind="bar", ax=ax)
    ax.set_xlabel("Tree Height (ft)")
    ax.set_ylabel("Tree Count")
    st.pyplot(fig)

    # Bar Chart: Tree Count vs Row
    st.write("### Tree Count vs Row")
    fig, ax = plt.subplots()
    row_group = filtered_data.groupby("Row")["Count"].sum()
    row_group.plot(kind="bar", ax=ax)
    ax.set_xlabel("Row")
    ax.set_ylabel("Tree Count")
    st.pyplot(fig)

with col2:
    # Display Image
    st.image("SPTF.png", width=300, output_format="auto")
    
    # Increase image size (3x bigger using markdown styling)
    st.markdown("""
    <style>
        img {
            transform: scale(1);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Overlay clickable buttons on image
    st.write("### Click on a Lot to Filter Data")
    colA, colB, colC = st.columns(3)
    
    lot_1 = colA.checkbox("Lot 1", value=True)
    lot_2 = colB.checkbox("Lot 2", value=True)
    all_lots = colC.checkbox("All Lots", value=False)
    
    selected_lots = []
    if lot_1:
        selected_lots.append(1)
    if lot_2:
        selected_lots.append(2)
    if all_lots or not selected_lots:
        filtered_data = data
    else:
        filtered_data = data[data["Lot"].isin(selected_lots)]

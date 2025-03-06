import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import msoffcrypto
import io

# Reduce side margins
st.set_page_config(layout="wide")

# Load data from Excel file
@st.cache_data
def load_data(password):
    file_path = "SPTF_Count.xlsx"
    
    with open(file_path, "rb") as file:
        decrypted = io.BytesIO()
        office_file = msoffcrypto.OfficeFile(file)
        
        # Check if file is encrypted
        try:
            office_file.load_key(password)
            office_file.decrypt(decrypted)
            return pd.read_excel(decrypted)
        except msoffcrypto.exceptions.DecryptionError:
            return pd.read_excel(file_path)  # Load normally if not encrypted

password = st.sidebar.text_input("Enter Excel Password", type="password")
enter_button = st.sidebar.button("Enter")

if enter_button:
    try:
        data = load_data(password)
        st.success("File loaded successfully!")
    except Exception as e:
        st.error("Incorrect password or file issue. Please try again.")
        st.stop()
else:
    st.warning("Please enter a password and click 'Enter' to load the Excel file.")
    st.stop()

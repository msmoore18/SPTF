import streamlit as st
import pandas as pd
import os
import msoffcrypto
import io
import openpyxl

def adjust_heights(df, year):
    increment = year - 2025  # Adjustments start from 2026
    df = df.copy()
    df["Tree Height (ft)"] = df["Tree Height (ft)"].apply(lambda x: x + increment if x > 2 else x + (increment * 0.5))
    return df

# Streamlit page configuration
st.set_page_config(layout="wide")

def load_data(password):
    file_path = "SPTF_count.xlsx"
    try:
        with open(file_path, "rb") as file:
            decrypted = io.BytesIO()
            office_file = msoffcrypto.OfficeFile(file)

            if not office_file.is_encrypted():
                return pd.read_excel(file_path, engine='openpyxl')

            office_file.load_key(password)
            office_file.decrypt(decrypted)
            return pd.read_excel(decrypted, engine='openpyxl')
    except Exception:
        return None

# User enters password
if "data" not in st.session_state:
    st.title("Enter Password to Access Data")

    def submit_password():
        password = st.session_state.password_input
        if password:
            data = load_data(password)
            if data is None:
                st.session_state["password_error"] = True
            else:
                st.session_state["data"] = data
                st.session_state["password_error"] = False

    # Initialize the error state
    if "password_error" not in st.session_state:
        st.session_state["password_error"] = False

    st.text_input(
        "Excel File Password:",
        type="password",
        key="password_input",
        on_change=submit_password
    )

    if st.button("Enter"):
        submit_password()

    # Handle errors or success after callback/button press
    if st.session_state.get("password_error"):
        st.error("Incorrect password or file issue. Please try again.")
    elif "data" in st.session_state:
        st.rerun()

    st.stop()

# Ensure data is available before proceeding
if "data" in st.session_state:
    df = st.session_state["data"]
    st.write("### Original Data:")
    st.dataframe(df)
    
    # Generate adjusted CSV files
    summary = {}
    for year in range(2026, 2031):
        adjusted_df = adjust_heights(df, year)
        adjusted_df.to_csv(f"{year}.csv", index=False)
        
        # Count tree heights for summary
        height_counts = adjusted_df.groupby("Tree Height (ft)")["Count"].sum().reset_index()
        summary[year] = dict(zip(height_counts["Tree Height (ft)"], height_counts["Count"]))

    # Convert summary to DataFrame
    summary_df = pd.DataFrame(summary).fillna(0).astype(int)
    st.write("### Initial Tree Count Summary")
    st.dataframe(summary_df)

    # User input for buying 1ft trees
    st.write("## Adjustments")
    for year in range(2026, 2031):
        buy_trees = st.number_input(f"Number of 1ft trees to buy in {year}", min_value=0, value=0, step=1)
        summary_df.loc[1, year] = summary_df.get(year, {}).get(1, 0) + buy_trees
    
    # User input for selling trees
    for year in range(2026, 2031):
        for height in summary_df.index:
            sell_trees = st.number_input(f"Number of {height}ft trees to sell in {year}", min_value=0, value=0, step=1)
            summary_df.loc[height, year] = max(0, summary_df.loc[height, year] - sell_trees)
    
    # Display updated summary
    st.write("### Updated Tree Count Summary")
    st.dataframe(summary_df)

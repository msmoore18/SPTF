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
    file_path = "SPTF_Count.xlsx"
    try:
        with open(file_path, "rb") as file:
            decrypted = io.BytesIO()
            office_file = msoffcrypto.OfficeFile(file)

            if not office_file.is_encrypted():
                return pd.read_excel(file_path, engine='openpyxl')

            office_file.load_key(password)
            office_file.decrypt(decrypted)
            return pd.read_excel(decrypted, engine='openpyxl')
    except msoffcrypto.exceptions.DecryptionError:
        return "Incorrect Password"
    except Exception as e:
        return f"Error: {e}"

# User enters password
if "data" not in st.session_state:
    st.title("Enter Password to Access Data")

    def submit_password():
        password = st.session_state.password_input
        if password:
            data = load_data(password)
            if data == "Incorrect Password":
                st.session_state["password_error"] = "Incorrect password. Please try again."
            elif isinstance(data, str) and data.startswith("Error:"):
                st.session_state["password_error"] = f"File issue: {data}"
            else:
                st.session_state["data"] = data
                st.session_state["password_error"] = None

    # Initialize the error state
    if "password_error" not in st.session_state:
        st.session_state["password_error"] = None

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
        st.error(st.session_state["password_error"])
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
    
    # Convert summary to DataFrame with proper structure
    all_heights = sorted(set(h for year in summary.values() for h in year.keys()))
    summary_df = pd.DataFrame(0, index=pd.Index(all_heights, dtype=int), columns=range(2026, 2031), dtype=int)
    
    for year, height_data in summary.items():
        for height, count in height_data.items():
            summary_df.at[int(height), year] = count
    
    st.write("### Initial Tree Count Summary")
    st.dataframe(summary_df)

    # User input for buying 1ft trees
    st.write("## Adjustments")
    for year in range(2026, 2031):
        buy_trees = st.number_input(f"Number of 1ft trees to buy in {year}", min_value=0, value=0, step=1)
        if 1 not in summary_df.index:
            summary_df.loc[1] = [0] * len(summary_df.columns)  # Initialize if missing
        summary_df.at[1, year] += buy_trees
    
    # User input for selling trees
    for year in range(2026, 2031):
        for height in summary_df.index:
            sell_trees = st.number_input(f"Number of {height}ft trees to sell in {year}", min_value=0, value=0, step=1)
            summary_df.at[height, year] = max(0, summary_df.at[height, year] - sell_trees)
    
    # Display updated summary
    st.write("### Updated Tree Count Summary")
    st.dataframe(summary_df)

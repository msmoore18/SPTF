import streamlit as st
import pandas as pd
import os
import openpyxl

def adjust_heights(df, year):
    increment = year - 2025  # Adjustments start from 2026
    df = df.copy()
    df["Tree Height (ft)"] = df["Tree Height (ft)"].apply(lambda x: x + increment if x > 2 else x + (increment * 0.5))
    return df

# Load the dataset
file_path = "SPTF_Count.xlsx"
if not os.path.exists(file_path):
    st.error("SPTF_count.xlsx not found! Please upload the file.")
else:
    st.write("### Enter Excel File Password:")
    password = st.text_input("Password", type="password")
    
    if password:
        try:
            df = pd.read_excel(file_path, engine='openpyxl', password=password)
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
        except Exception as e:
            st.error(f"Failed to open file: {e}")

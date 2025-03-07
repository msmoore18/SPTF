import numpy as np
import pandas as pd
import streamlit as st

def generate_tree_table(b30, o_values):
    """
    Generates a tree growth table based on provided values.
    
    Parameters:
    - b30 (float): Number of trees to buy each year.
    - o_values (list of float): Values for O2:O27 affecting tree reductions.
    
    Returns:
    - pd.DataFrame: Computed tree growth table.
    """
    # Hardcoded B2:B27 values based on provided data
    b_values = np.array([
        0, 10646, 13536, 3487, 1382, 659, 654, 537, 495, 357,
        235, 150, 84, 53, 33, 26, 34, 38, 59, 47,
        62, 90, 152, 157, 139, 278
    ])
    
    # Ensure correct input length
    if len(o_values) != 26:
        raise ValueError("Expected exactly 26 values for O2:O27.")
    
    # Define column headers
    column_headers = ["", "Tree Height (ft)"] + list(range(2025, 2035 + 1))
    
    # Initialize the output table with column headers
    output_table = pd.DataFrame(index=range(27), columns=column_headers)
    
    # Set the first column as tree height values
    output_table.iloc[1:27, 1] = b_values
    
    # Fill the first row (C2:L2) with B30
    output_table.iloc[1, 2:] = b30
    
    # Fill C3:L27 based on the given formula: IF($O2<=B2,B2-$O2,B2-B2)
    for row in range(2, 27):  # Row indices corresponding to 3-27 in Excel
        for col_idx, col in enumerate(range(2, len(column_headers))):  # Column indices corresponding to years
            b_value = b_values[row - 2]  # B2:B27 values
            o_value = o_values[row - 2]  # O2:O27 values
            
            # Apply the formula
            if o_value <= b_value:
                output_table.iloc[row, col] = b_value - o_value
            else:
                output_table.iloc[row, col] = 0
    
    # Convert table values to numeric (handling NaNs)
    output_table = output_table.apply(pd.to_numeric, errors='coerce')
    
    return output_table

# Streamlit App
st.title("Tree Growth Table Generator")

# User input for B30
b30 = st.number_input("Enter the number of trees to buy each year (B30):", min_value=0.0, step=1.0, value=1000.0)

# User input for O2:O27 values
o_values = []
st.write("Enter 26 values for O2:O27:")
for i in range(26):
    o_value = st.number_input(f"O{i+2}:", min_value=0.0, step=1.0, value=500.0, key=f"o_{i}")
    o_values.append(o_value)

# Generate and display the table if all inputs are provided
if st.button("Generate Table"):
    table = generate_tree_table(b30, o_values)
    st.write("Generated Tree Table:")
    st.dataframe(table)

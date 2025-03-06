import streamlit as st
import pandas as pd
import numpy as np

# Load initial data
tree_data = {
    1: 3901, 1.5: 6745, 2: 7427, 2.5: 6109, 3: 3487, 4: 1382, 5: 659, 6: 654, 7: 537, 8: 495, 9: 357, 
    10: 235, 11: 150, 12: 84, 13: 53, 14: 33, 15: 26, 16: 34, 17: 38, 18: 59, 19: 47, 20: 62, 
    21: 90, 22: 152, 23: 157, 24: 139, 25: 278, 26: 276
}
df = pd.DataFrame(list(tree_data.items()), columns=["Tree Height (ft)", "Count"])

# User inputs for growth rate, mortality rate, and sellable inventory
st.sidebar.header("User Inputs")

growth_rates = {
    "0-5ft": st.sidebar.number_input("Growth Rate (ft) for 0-5ft", min_value=0.0, value=1.0),
    "6-10ft": st.sidebar.number_input("Growth Rate (ft) for 6-10ft", min_value=0.0, value=1.0),
    "11-15ft": st.sidebar.number_input("Growth Rate (ft) for 11-15ft", min_value=0.0, value=1.0),
    "16-20ft": st.sidebar.number_input("Growth Rate (ft) for 16-20ft", min_value=0.0, value=1.0),
    ">20ft": st.sidebar.number_input("Growth Rate (ft) for >20ft", min_value=0.0, value=1.0),
}

mortality_rates = {
    "0-5ft": st.sidebar.number_input("Mortality Rate (%) for 0-5ft", min_value=0.0, value=5.0),
    "6-10ft": st.sidebar.number_input("Mortality Rate (%) for 6-10ft", min_value=0.0, value=3.0),
    "11-15ft": st.sidebar.number_input("Mortality Rate (%) for 11-15ft", min_value=0.0, value=2.0),
    "16-20ft": st.sidebar.number_input("Mortality Rate (%) for 16-20ft", min_value=0.0, value=1.5),
    ">20ft": st.sidebar.number_input("Mortality Rate (%) for >20ft", min_value=0.0, value=1.0),
}

sellable_inventory = {
    "0-5ft": st.sidebar.number_input("Sellable Inventory for 0-5ft", min_value=0, value=0),
    "6-10ft": st.sidebar.number_input("Sellable Inventory for 6-10ft", min_value=0, value=100),
    "11-15ft": st.sidebar.number_input("Sellable Inventory for 11-15ft", min_value=0, value=150),
    "16-20ft": st.sidebar.number_input("Sellable Inventory for 16-20ft", min_value=0, value=200),
    ">20ft": st.sidebar.number_input("Sellable Inventory for >20ft", min_value=0, value=250),
}

# Function to simulate tree growth and mortality
def simulate_growth(df, years=10):
    yearly_new_plantings = []
    yearly_trees_sold = []
    
    for year in range(1, years + 1):
        new_tree_data = df.copy()
        new_tree_data["Next Year Count"] = 0
        
        for i, row in df.iterrows():
            height = row["Tree Height (ft)"]
            count = row["Count"]
            
            # Determine growth category
            if height <= 5:
                growth_rate = growth_rates["0-5ft"]
                mortality_rate = mortality_rates["0-5ft"]
                sellable_count = sellable_inventory["0-5ft"]
            elif height <= 10:
                growth_rate = growth_rates["6-10ft"]
                mortality_rate = mortality_rates["6-10ft"]
                sellable_count = sellable_inventory["6-10ft"]
            elif height <= 15:
                growth_rate = growth_rates["11-15ft"]
                mortality_rate = mortality_rates["11-15ft"]
                sellable_count = sellable_inventory["11-15ft"]
            elif height <= 20:
                growth_rate = growth_rates["16-20ft"]
                mortality_rate = mortality_rates["16-20ft"]
                sellable_count = sellable_inventory["16-20ft"]
            else:
                growth_rate = growth_rates[">20ft"]
                mortality_rate = mortality_rates[">20ft"]
                sellable_count = sellable_inventory[">20ft"]

            # Apply mortality rate
            survivors = count * (1 - mortality_rate / 100)
            
            # Move trees to the next height category
            new_height = height + growth_rate
            if new_height in new_tree_data["Tree Height (ft)"].values:
                new_tree_data.loc[new_tree_data["Tree Height (ft)"] == new_height, "Next Year Count"] += survivors
            else:
                new_tree_data = new_tree_data.append({"Tree Height (ft)": new_height, "Next Year Count": survivors}, ignore_index=True)

            # Apply selling of trees
            trees_sold = min(sellable_count, survivors)
            new_tree_data.loc[new_tree_data["Tree Height (ft)"] == height, "Next Year Count"] -= trees_sold

        # Calculate number of new trees (1ft) needed to maintain inventory
        total_inventory = new_tree_data["Next Year Count"].sum()
        initial_inventory = df["Count"].sum()
        new_trees_needed = max(0, initial_inventory - total_inventory)
        
        yearly_new_plantings.append(new_trees_needed)
        yearly_trees_sold.append(sum(sellable_inventory.values()))

        # Update data for next iteration
        df = new_tree_data[["Tree Height (ft)", "Next Year Count"]].rename(columns={"Next Year Count": "Count"})
    
    return yearly_new_plantings, yearly_trees_sold

# Run the simulation
new_trees_needed, trees_sold = simulate_growth(df, years=10)

# Display results
st.header("Tree Growth & Selling Predictions for the Next 10 Years")

result_df = pd.DataFrame({
    "Year": range(1, 11),
    "New Trees to Plant": new_trees_needed,
    "Trees to Sell": trees_sold
})

st.write(result_df)

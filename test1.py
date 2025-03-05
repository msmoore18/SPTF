import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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
fig, ax = plt.subplots()
data.groupby("Lot")["Height"].sum().plot(kind="bar", ax=ax)
ax.set_xlabel("Lot Number")
ax.set_ylabel("Total Tree Height")
st.pyplot(fig)

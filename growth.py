import streamlit as st
import pandas as pd
import plotly.express as px
import msoffcrypto
import io

st.set_page_config(layout="wide")

def load_data(password):
    file_path = "SPTF_Count.xlsx"
    try:
        with open(file_path, "rb") as file:
            decrypted = io.BytesIO()
            office_file = msoffcrypto.OfficeFile(file)
            if not office_file.is_encrypted():
                return pd.read_excel(file_path)
            office_file.load_key(password)
            office_file.decrypt(decrypted)
            return pd.read_excel(decrypted)
    except Exception:
        return None

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

    st.text_input("Excel File Password:", type="password", key="password_input", on_change=submit_password)
    if st.button("Enter"):
        submit_password()
    if st.session_state.get("password_error"):
        st.error("Incorrect password or file issue. Please try again.")
    elif "data" in st.session_state:
        st.rerun()
    st.stop()

data = st.session_state["data"]

def project_tree_growth(data, years=10):
    projection = data.copy()
    for year in range(1, years + 1):
        projection[f'Year {2025 + year}'] = projection['Tree Height (ft)'].apply(lambda x: x + 1 if x > 2 else x + 0.5)
    return projection

def update_with_new_trees(projection, years=10, new_trees_per_year=0):
    new_tree_entries = []
    for year in range(1, years + 1):
        new_tree_entries.append({
            'Tree Height (ft)': 0.5,
            f'Year {2025 + year}': 0.5,
            'Lot': 'N/A',
            'Row': 'N/A',
            'Quality': 'N/A',
            'Count': new_trees_per_year
        })
    return pd.concat([projection, pd.DataFrame(new_tree_entries)], ignore_index=True)

def apply_sales(projection, years=10, sales={}):
    for year_col in sales:
        if year_col in projection.columns:
            projection[year_col] = projection[year_col] - sales[year_col]
            projection[year_col] = projection[year_col].clip(lower=0)
    return projection

def create_summary(projection, years=10):
    summary = projection.groupby("Tree Height (ft)")[[f'Year {2025 + i}' for i in range(1, years + 1)]].sum().reset_index()
    return summary

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Lot Map", "Tree Inventory", "Projected Tree Inventory", "Tree Maintenance"])

if page == "Lot Map":
    st.title("Lot Map")
    st.image("map_larger.png")

if page == "Tree Inventory":
    st.title("2025 Inventory for Spruce Point Tree Farm")
    st.markdown(f"<h3 style='color:green;'>Total Tree Count Based on Filter Selections: {filtered_data['Count'].sum()}</h3>", unsafe_allow_html=True)

    # Tree Count vs Tree Height
    height_group = filtered_data.groupby("Tree Height (ft)")["Count"].sum()
    fig = px.bar(height_group.reset_index(), x='Tree Height (ft)', y='Count', 
                 labels={'Tree Height (ft)': 'Tree Height (ft)', 'Count': 'Tree Count'})
    fig.update_layout(xaxis=dict(tickmode='array', tickvals=height_group.index))
    st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
    st.plotly_chart(fig)
    st.markdown('</div>', unsafe_allow_html=True)

    # Pie Chart
    height_bins = pd.cut(filtered_data["Tree Height (ft)"], bins=[0, 5, 10, 15, 20, float('inf')], 
                         labels=["0-5ft", "6-10ft", "11-15ft", "16-20ft", ">20ft"])
    height_distribution = filtered_data.groupby(height_bins)["Count"].sum().reset_index()
    fig = px.pie(height_distribution, names="Tree Height (ft)", values="Count")
    fig.update_layout(legend=dict(x=.1, y=0.5))
    st.plotly_chart(fig)

    # Tree Count vs Lot (only appears if selected_lot == 'All')
    if selected_lot == 'All':
        lot_group = filtered_data.groupby("Lot")["Count"].sum().reset_index()
        fig_lot = px.bar(lot_group, x='Lot', y='Count',
                         labels={'Lot': 'Lot', 'Count': 'Tree Count'})
        fig_lot.update_layout(xaxis=dict(type='category'))
    
        st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
        st.plotly_chart(fig_lot)
        st.markdown('</div>', unsafe_allow_html=True)

    # Tree Count vs Row (only appears if selected_lot does not = 'All')
    if selected_lot != 'All':
        lot_group = filtered_data.groupby("Row")["Count"].sum().reset_index()
        fig_lot = px.bar(lot_group, x='Row', y='Count',
                         labels={'Row': 'Row', 'Count': 'Tree Count'})
        fig_lot.update_layout(xaxis=dict(type='category'))
    
        st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
        st.plotly_chart(fig_lot)
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "Tree Maintenance":
    st.title("Tree Maintenance Table")
    st.markdown(f"<h3 style='color:green;'>Total Tree Count Based on Filter Selections: {filtered_data['Count'].sum()}</h3>", unsafe_allow_html=True)
    st.write("This page lets you customize and download a printable table for Rudy. Use the filters on the left to select which Quality (B: Needs Pruning, C: Needs to be cut), Lot #, and Tree Height you want displayed in the table")

    # Filtered summary of trees
    tree_summary = filtered_data.groupby(["Quality", "Lot", "Row", "Tree Height (ft)"])['Count'].sum().reset_index()
    tree_summary["Work Completed?"] = ""

    # Display table
    csv = tree_summary.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Table as CSV",
        data=csv,
        file_name="tree_summary.csv",
        mime="text/csv"
    )
    st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
    st.dataframe(tree_summary, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Projected Tree Inventory":
    st.title("Projected Tree Inventory")
    projected_data = project_tree_growth(data)
    new_trees_per_year = st.number_input("How many 6-inch trees to add per year?", min_value=0, step=1)
    projected_data = update_with_new_trees(projected_data, new_trees_per_year=new_trees_per_year)
    
    st.subheader("Specify Sales Numbers")
    sales = {}
    for year in range(1, 11):
        sales[f'Year {2025 + year}'] = st.number_input(f"Trees to sell in {2025 + year}", min_value=0, step=1)
    projected_data = apply_sales(projected_data, sales=sales)
    
    summary_data = create_summary(projected_data)
    st.dataframe(summary_data)

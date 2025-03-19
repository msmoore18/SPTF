# Ensure data is available before proceeding
if "data" in st.session_state:
    data = st.session_state["data"]
else:
    st.stop()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Lot Map", "Tree Inventory", "Tree Maintenance"])

# Show filter options only if not on the "Lot Map" page
if page != "Lot Map":
    st.sidebar.header("Filter Options")
    height_range = st.sidebar.slider(
        "Select Tree Height Range (ft)",
        float(data["Tree Height (ft)"].min()),
        float(data["Tree Height (ft)"].max()),
        (
            float(data["Tree Height (ft)"].min()), 
            float(data["Tree Height (ft)"].max())
        ),
        0.5
    )

    # Ensure "OC" is included in the quality filter
    quality_options = st.sidebar.multiselect(
        "Select Quality",
        options=data["Quality"].unique(),
        default=[q for q in data["Quality"].unique() if q in ["A", "B", "C", "OC"]]
    )

    lot_options = ['All'] + sorted(data["Lot"].unique(), key=lambda x: int(str(x)))
    selected_lot = st.sidebar.selectbox("Select Lot", options=lot_options)
    if selected_lot == 'All':
        lots = data["Lot"].unique()
    else:
        lots = [selected_lot]

    # Filter data based on selections
    filtered_data = data[
        (data["Lot"].isin(lots)) & 
        (data["Tree Height (ft)"].between(height_range[0], height_range[1])) & 
        (data["Quality"].isin(quality_options))
    ]

if page == "Tree Inventory":
    st.title("2025 Inventory for Spruce Point Tree Farm")
    st.markdown(f"<h3 style='color:green;'>Total Tree Count Based on Filter Selections: {filtered_data['Tree Count'].sum()}</h3>", unsafe_allow_html=True)

    # Tree Count vs Tree Height
    height_group = filtered_data.groupby("Tree Height (ft)")["Tree Count"].sum()
    fig = px.bar(height_group.reset_index(), x='Tree Height (ft)', y='Tree Count', 
                 labels={'Tree Height (ft)': 'Tree Height (ft)', 'Tree Count': 'Tree Count'})
    fig.update_layout(xaxis=dict(tickmode='array', tickvals=height_group.index))
    st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
    st.plotly_chart(fig)
    st.markdown('</div>', unsafe_allow_html=True)

    # Pie Chart
    height_bins = pd.cut(filtered_data["Tree Height (ft)"], bins=[0, 5, 10, 15, 20, float('inf')], 
                         labels=["0-5ft", "6-10ft", "11-15ft", "16-20ft", ">20ft"])
    height_distribution = filtered_data.groupby(height_bins)["Tree Count"].sum().reset_index()
    fig = px.pie(height_distribution, names="Tree Height (ft)", values="Tree Count")
    fig.update_layout(legend=dict(x=.1, y=0.5))
    st.plotly_chart(fig)

    # Tree Count vs Lot (only appears if selected_lot == 'All')
    if selected_lot == 'All':
        lot_group = filtered_data.groupby("Lot")["Tree Count"].sum().reset_index()
        fig_lot = px.bar(lot_group, x='Lot', y='Tree Count',
                         labels={'Lot': 'Lot', 'Tree Count': 'Tree Count'})
        fig_lot.update_layout(xaxis=dict(type='category'))
    
        st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
        st.plotly_chart(fig_lot)
        st.markdown('</div>', unsafe_allow_html=True)

    # Tree Count vs Row (only appears if selected_lot does not = 'All')
    if selected_lot != 'All':
        lot_group = filtered_data.groupby("Row")["Tree Count"].sum().reset_index()
        fig_lot = px.bar(lot_group, x='Row', y='Tree Count',
                         labels={'Row': 'Row', 'Tree Count': 'Tree Count'})
        fig_lot.update_layout(xaxis=dict(type='category'))
    
        st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
        st.plotly_chart(fig_lot)
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "Tree Maintenance":
    st.title("Tree Maintenance Table")
    st.markdown(f"<h3 style='color:green;'>Total Tree Count Based on Filter Selections: {filtered_data['Tree Count'].sum()}</h3>", unsafe_allow_html=True)
    st.write("This page lets you customize and download a printable table for Rudy. Use the filters on the left to select which Quality (B: Needs Pruning, C: Needs to be cut, OC: Overcrowding), Lot #, and Tree Height you want displayed in the table")

    # Filtered summary of trees
    tree_summary = filtered_data.groupby(["Quality", "Lot", "Row", "Tree Height (ft)"])['Tree Count'].sum().reset_index()
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

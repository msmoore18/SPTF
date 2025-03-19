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

    quality_options = st.sidebar.multiselect(
        "Select Quality",
        options=data["Quality"].unique(),
        default=data["Quality"].unique()
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

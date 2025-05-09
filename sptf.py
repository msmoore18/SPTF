# Planting History
elif page == "Planting History":
    st.title("Planting History")

    planting_data = sheets["Planting"].copy()
    planting_data["Date"] = pd.to_datetime(planting_data["Date"])
    planting_data["Year"] = planting_data["Date"].dt.year

    # Use only valid numeric height columns for melting
    id_columns = ["Date", "Year", "Lot #", "Row #"]
    height_columns = [col for col in planting_data.columns if col not in id_columns and str(col).strip().isdigit()]

    long_df = planting_data.melt(
        id_vars=id_columns,
        value_vars=height_columns,
        var_name="Tree Height (in)",
        value_name="Count"
    )

    # Clean and filter
    long_df["Tree Height (in)"] = pd.to_numeric(long_df["Tree Height (in)"], errors="coerce")
    long_df = long_df.dropna(subset=["Tree Height (in)", "Count"])
    long_df["Count"] = long_df["Count"].astype(int)

    # Sidebar filters
    st.sidebar.header("Planting Filters")
    min_height = int(long_df["Tree Height (in)"].min())
    max_height = int(long_df["Tree Height (in)"].max())
    height_range = st.sidebar.slider("Tree Height Range (in)", min_height, max_height, (min_height, max_height), step=6)

    lot_options = ["All"] + sorted(long_df["Lot #"].dropna().unique(), key=lambda x: int(str(x)))
    selected_lot = st.sidebar.selectbox("Select Lot", lot_options)

    # Apply filters
    filtered = long_df[long_df["Tree Height (in)"].between(height_range[0], height_range[1])]
    if selected_lot != "All":
        filtered = filtered[filtered["Lot #"] == selected_lot]

    # Plot 1: Trees Planted by Height and Year
    grouped = filtered.groupby(["Tree Height (in)", "Year"])["Count"].sum().reset_index()
    fig1 = px.bar(
        grouped,
        x="Tree Height (in)",
        y="Count",
        color="Year",
        title="Trees Planted by Height and Year",
        labels={"Count": "Trees Planted"}
    )
    fig1.update_layout(barmode="group")
    st.plotly_chart(fig1)

    # Plot 2: Pie Chart of Tree Heights
    pie_data = filtered.groupby("Tree Height (in)")["Count"].sum().reset_index()
    fig2 = px.pie(pie_data, names="Tree Height (in)", values="Count", title="Distribution of Trees by Height (in)")
    st.plotly_chart(fig2)

    # Plot 3: Bar by Lot or Row
    if selected_lot == "All":
        lot_group = filtered.groupby("Lot #")["Count"].sum().reset_index()
        fig3 = px.bar(lot_group, x="Lot #", y="Count", title="Trees Planted by Lot", labels={"Count": "Trees Planted"})
    else:
        row_group = filtered.groupby("Row #")["Count"].sum().reset_index()
        fig3 = px.bar(row_group, x="Row #", y="Count", title=f"Trees Planted by Row in Lot {selected_lot}", labels={"Count": "Trees Planted"})
    st.plotly_chart(fig3)

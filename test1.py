
        label="Download Table as CSV",
        data=csv,
        file_name="tree_summary.csv",
        mime="text/csv"
    )
    st.dataframe(tree_summary, hide_index=True)

elif page == "SPTF Lot Map":
    st.title("SPTF Lot Map")
    st.image("SPTF.png", width=600)

elif page == "Tree Maintenance":
    st.title("Tree Maintenance Table")
    st.write("Use this page to download a printable table for Rudy. Use the filters on the left to select which Quality (B: Needs Pruning, C: Needs to be cut), Lot #, and Tree Height you want displayed in the table")
    
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
    st.dataframe(tree_summary, hide_index=True)
    
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
    st.dataframe(tree_summary, hide_index=True)
    
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
    st.dataframe(tree_summary, hide_index=True)
    
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
    st.dataframe(tree_summary, hide_index=True)
    
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
    st.dataframe(tree_summary, hide_index=True)(B: Needs Pruning, C: Needs to be cut), Lot #, and Tree Height you want displayed in the table")
    
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
    st.dataframe(tree_summary, hide_index=True)
    
    

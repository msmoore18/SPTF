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
    st.dataframe(tree_summary, hide_index=True)
    
    

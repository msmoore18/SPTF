import streamlit as st
import pandas as pd
import plotly.express as px
import msoffcrypto
import io
import openpyxl

# Streamlit page configuration
st.set_page_config(layout="wide")

# Load password-protected Excel file
def load_data(password):
    file_path = "SPTF_Count.xlsx"
    try:
        with open(file_path, "rb") as file:
            decrypted = io.BytesIO()
            office_file = msoffcrypto.OfficeFile(file)

            if not office_file.is_encrypted():
                return pd.ExcelFile(file_path)

            office_file.load_key(password)
            office_file.decrypt(decrypted)
            return pd.ExcelFile(decrypted)
    except Exception:
        return None

# Ensure session state variables exist
if "password_input" not in st.session_state:
    st.session_state["password_input"] = ""

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
                st.session_state["password"] = password  # Store password in session
                st.session_state["password_error"] = False

    # Initialize the error state
    if "password_error" not in st.session_state:
        st.session_state["password_error"] = False

    st.text_input(
        "Excel File Password:",
        type="password",
        key="password_input",
        on_change=submit_password
    )

    if st.button("Enter"):
        submit_password()

    # Handle errors or success after callback/button press
    if st.session_state.get("password_error"):
        st.error("Incorrect password or file issue. Please try again.")
    elif "data" in st.session_state:
        st.rerun()

    st.stop()

# Ensure data is available before proceeding
if "data" in st.session_state and "password" in st.session_state:
    xls = st.session_state["data"]
    excel_password = st.session_state["password"]  # Retrieve stored password
else:
    st.stop()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Lot Map", "Tree Inventory", "Projected Tree Inventory", "Tree Maintenance"])

if page == "Projected Tree Inventory":
    st.title("Projected Tree Inventory")

    # Load the "calculations" sheet with decryption
    file_path = "SPTF_Count.xlsx"
    
    with open(file_path, "rb") as file:
        decrypted = io.BytesIO()
        office_file = msoffcrypto.OfficeFile(file)
        office_file.load_key(excel_password)  # Use stored password
        office_file.decrypt(decrypted)
    
    wb = openpyxl.load_workbook(decrypted, data_only=True)
    ws = wb["calculations"]

    # User input fields for B30 and O12
    user_input_b30 = st.number_input("Enter value for B30", value=ws["B30"].value or 0)
    user_input_o12 = st.number_input("Enter value for O12", value=ws["O12"].value or 0)

    if st.button("Update Calculations"):
        ws["B30"].value = user_input_b30
        ws["O12"].value = user_input_o12

        # Save the updated file
        excel_modified = io.BytesIO()
        wb.save(excel_modified)
        excel_modified.seek(0)

        # Reload updated calculations
        updated_wb = openpyxl.load_workbook(excel_modified, data_only=True)
        updated_ws = updated_wb["calculations"]

        # Extract the A1:L28 range as a DataFrame
        data_range = []
        for row in updated_ws.iter_rows(min_row=1, max_row=28, min_col=1, max_col=12, values_only=True):
            data_range.append(row)
        
        df_calculations = pd.DataFrame(data_range)

        st.success("Excel file updated successfully!")

        # Display updated table
        import ace_tools as tools
        tools.display_dataframe_to_user(name="Updated Calculations", dataframe=df_calculations)

        # Provide a download option for the updated Excel file
        st.download_button(
            label="Download Updated Excel",
            data=excel_modified,
            file_name="Updated_SPTF_Count.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

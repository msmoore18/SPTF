import streamlit as st
import pandas as pd
import openpyxl
import io
import msoffcrypto

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

# User enters password
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
        st.rerun()  # Now outside the callback, safe to call

    st.stop()

# Ensure data is available before proceeding
if "data" in st.session_state:
    xls = st.session_state["data"]
else:
    st.stop()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Lot Map", "Tree Inventory", "Projected Tree Inventory", "Tree Maintenance"])

if page == "Projected Tree Inventory":
    st.title("Projected Tree Inventory")

    # Load the "calculations" sheet
    with pd.ExcelWriter("SPTF_Count.xlsx", engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
        wb = writer.book
        ws = wb["calculations"]

        # Get user input
        user_input_b30 = st.number_input("Enter value for B30", value=ws["B30"].value or 0)
        user_input_o12 = st.number_input("Enter value for O12", value=ws["O12"].value or 0)

        # Update values in the sheet
        ws["B30"].value = user_input_b30
        ws["O12"].value = user_input_o12

        # Save updated workbook
        excel_modified = io.BytesIO()
        wb.save(excel_modified)
        excel_modified.seek(0)

        # Load updated values
        df_calculations = pd.read_excel(excel_modified, sheet_name="calculations", usecols="A:L", nrows=28)

    # Display updated data
    st.write("### Updated Calculations Table")
    import ace_tools as tools
    tools.display_dataframe_to_user(name="Updated Calculations", dataframe=df_calculations)

    # Provide download option
    st.download_button(
        label="Download Updated Excel",
        data=excel_modified,
        file_name="Updated_SPTF_Count.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

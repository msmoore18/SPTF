# Copilot Instructions - SPTF (Spruce Point Tree Farm)

## Project Overview
SPTF is a Streamlit-based web application for managing tree farm inventory, sales tracking, and planting history. The app reads from a password-protected Excel file (`SPTF_Inventory_25.xlsx`) containing multiple sheets: Inventory, Sales, and Planting.

## Architecture & Key Components

### Data Flow
1. **Password-Protected Access** (`sptf.py`, lines 10-26): `load_data()` decrypts the Excel file using `msoffcrypto` library before processing
2. **Session State Management**: Password unlocks Excel data stored in `st.session_state["data"]` as a dict of DataFrames (one per sheet)
3. **Multi-Page Navigation**: Sidebar radio button routes between four pages - "Current Inventory", "Historical Sales", "Planting History", "Lot Map"

### Critical Patterns

#### Session State for Data Persistence
```python
# Data is stored at module level after password unlock
if "data" in st.session_state:
    sheets = st.session_state["data"]  # Dict with keys: "Inventory", "Sales", "Planting"
    data = sheets["Inventory"]
```
**Key**: Always check `"data" in st.session_state` before accessing sheets - app calls `st.stop()` if missing.

#### Streamlit Widget Key Management
Widget state collisions are prevented using unique keys:
- `key="inventory_height_slider_unique"` (line 73)
- `key="sales_height_slider_unique"` (line 163)
- `key="planting_height_slider_unique"` (line 272)

**Reason**: Multiple sliders with same range on different pages would share state without unique keys.

#### Data Filtering Pattern
Three pages use consistent multi-select filter pattern:
- Height range slider (feet or inches depending on page)
- Quality dropdown (A/B/C/OC for Inventory; A/B for Sales)
- Lot/Customer selection
- Apply filters with pandas `.isin()` and `.between()` before visualization

#### Historical Sales Pre-2023 Logic
Sales data before 2023 lacks Quality and Customer detail - handled by disabling filters:
```python
any_pre_2023 = any(yr < 2023 for yr in selected_years)
if any_pre_2023:
    st.sidebar.multiselect(..., disabled=True)
```

### Data Transformations

**Planting Page** (lines 240-280): Unpivots numeric columns (tree heights in inches) to long format:
- Original: columns "12", "18", "24" (height in inches) with tree counts
- Transformed: 3-column structure `[Date, Tree Height (in), Count]` for plotting

**Inventory Page** (line 125): Quality order is `["A", "B", "C", "OC"]` - maintain this order when filtering.

## Development Workflows

### Running the App
```bash
streamlit run sptf.py
```
App runs on `http://localhost:8501` and requires Excel password at startup.

### Modifying Pages
- Add new page by adding condition to page routing (line 69)
- Follow existing filter pattern: sidebar filters → apply with pandas → display charts → show summary dataframe
- Use `st.markdown(..., unsafe_allow_html=True)` for green styled metrics (see lines 99, 148)

### Adding New Excel Sheets
1. Ensure sheet is in `SPTF_Inventory_25.xlsx`
2. Add new page with pattern: `sheets["NewSheet"]` after checking session state
3. Use unique slider/selectbox keys if adding interactive filters

## Dependencies
- **streamlit**: Web framework
- **pandas**: Data manipulation (critical for sheet loading and filtering)
- **plotly**: Interactive charts (bar, pie)
- **msoffcrypto-tool**: Decrypts password-protected Excel files
- **openpyxl**: Not currently used (archived code reference)
- **xlwings**: Not currently used (archived code reference)

See `requirements.txt` for pinned versions.

## Important Notes
- **No error recovery after password failure**: Wrong password shows error but doesn't allow retry gracefully - user must refresh page
- **Map image**: Lot Map page displays `map_larger.png` - ensure file exists in root directory
- **Archived code**: `growth_archived.py` and `test1_archived.py` are older versions using different Excel sources - reference for historical patterns only

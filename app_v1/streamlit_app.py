# # streamlit_app.py
# import streamlit as st
# import pandas as pd
# import io
# import hashlib

# from code_52_26_wks import (
#     preprocessing_excel,
#     identify_opportunities,
#     preprocessing_value_drivers,
#     merging_data,
#     calculate_value_driver_contributions,
#     identify_risks,
# )

# st.set_page_config(page_title="P&G Growth Opportunities & Risks", layout="wide")

# # -------------------------
# # Session-state bootstrapping
# # -------------------------
# if "uploaded_file_hash" not in st.session_state:
#     st.session_state.uploaded_file_hash = None
# if "sheets_confirmed" not in st.session_state:
#     st.session_state.sheets_confirmed = False
# if "selected_sheet1" not in st.session_state:
#     st.session_state.selected_sheet1 = None
# if "selected_sheet2" not in st.session_state:
#     st.session_state.selected_sheet2 = None
# if "brand_owner" not in st.session_state:
#     st.session_state.brand_owner = None

# # -------------------------
# # Custom styling for the app
# # -------------------------
# st.markdown(
#     """
#     <style>
#     .main-header {
#         background: linear-gradient(135deg, #1f7a3c 0%, #2d9e52 100%);
#         padding: 25px;
#         border-radius: 10px;
#         margin-bottom: 20px;
#     }
#     .main-header h1 {
#         color: white;
#         margin: 0;
#         font-size: 2.5rem;
#     }
#     .main-header p {
#         color: #e8f5e9;
#         margin: 10px 0 0 0;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# st.markdown(
#     """
#     <div class="main-header">
#         <h1>Growth Opportunities & Risks Analysis</h1>
#         <p>Upload your raw Excel workbook and get instant insights on priority brands and risk assessment</p>
#     </div>
#     """,
#     unsafe_allow_html=True
# )

# st.markdown("---")

# uploaded_file = st.file_uploader("Choose Excel file", type=["xls", "xlsx"])

# st.markdown("### ⚙️ Configuration")
# col1, col2 = st.columns(2)
# with col1:
#     tangible_threshold = st.number_input(
#         "Tangible threshold (Latest 52 Wks > ?)",
#         min_value=0.0,
#         value=2.0
#     )
# with col2:
#     growing_threshold = st.number_input(
#         "Growing penetration threshold (Latest 26 vs YA > ?)",
#         min_value=0.0,
#         value=0.2
#     )

# # ---------------------------------
# # If a file has been uploaded...
# # ---------------------------------
# if uploaded_file is None:
#     st.info("Please upload an Excel file to begin.")
#     st.stop()

# # Cache file bytes once; create fresh BytesIO for every read
# file_bytes = uploaded_file.getvalue()
# def fresh_io():
#     return io.BytesIO(file_bytes)

# # Hash to detect new file and reset state when file changes
# file_hash = hashlib.md5(file_bytes).hexdigest()[:8]
# if st.session_state.uploaded_file_hash != file_hash:
#     # New file: reset sheet + brand owner choices
#     st.session_state.uploaded_file_hash = file_hash
#     st.session_state.sheets_confirmed = False
#     st.session_state.selected_sheet1 = None
#     st.session_state.selected_sheet2 = None
#     st.session_state.brand_owner = None

# # Get sheets from file
# try:
#     xls = pd.ExcelFile(fresh_io())
#     raw_sheets = xls.sheet_names
# except Exception as e:
#     st.error(f"Couldn't open the Excel file: {e}")
#     st.stop()

# # ---------------------------------
# # Sheet selection gate (one-time)
# # ---------------------------------
# if not st.session_state.sheets_confirmed:
#     st.markdown("### 📄 Sheet Selection")

#     # Smart detection
#     default_sheet1_idx = 0  # Because [None] is index 0 in the selection below
#     default_sheet2_idx = 0
#     detected_sheet1 = None
#     detected_sheet2 = None

#     for idx, sheet_name in enumerate(raw_sheets):
#         sheet_name_upper = sheet_name.upper()
#         if "PENETRATION" in sheet_name_upper and detected_sheet1 is None:
#             default_sheet1_idx = idx + 1  # shift by 1 for the [None] option
#             detected_sheet1 = sheet_name
#         if "KPI" in sheet_name_upper and detected_sheet2 is None:
#             default_sheet2_idx = idx + 1
#             detected_sheet2 = sheet_name

#     if detected_sheet1:
#         st.success(f"✓ Auto-detected Penetration sheet: **{detected_sheet1}**")
#     if detected_sheet2:
#         st.success(f"✓ Auto-detected KPI sheet: **{detected_sheet2}**")

#     # Use content hash as part of form key to reset on actual file change
#     form_key = f"sheet_form_{file_hash}"

#     with st.form(key=form_key):
#         sheet1_choice = st.selectbox(
#             "Select the sheet for penetration trends",
#             options=[None] + raw_sheets,
#             index=default_sheet1_idx,
#             format_func=lambda x: "" if x is None else x,
#         )
#         sheet2_choice = st.selectbox(
#             "Select the sheet for value drivers",
#             options=[None] + raw_sheets,
#             index=default_sheet2_idx,
#             format_func=lambda x: "" if x is None else x,
#         )
#         submit_sheets = st.form_submit_button("Load sheets")

#     if not submit_sheets:
#         st.info("Please choose the two sheets above and press **Load sheets** to start.")
#         st.stop()

#     if sheet1_choice is None or sheet2_choice is None:
#         st.error("❌ Please select both sheets before submitting.")
#         st.stop()

#     if sheet1_choice == sheet2_choice:
#         st.error("❌ Penetration and value driver sheets must be different.")
#         st.stop()

#     # Persist and continue
#     st.session_state.selected_sheet1 = sheet1_choice
#     st.session_state.selected_sheet2 = sheet2_choice
#     st.session_state.sheets_confirmed = True
#     # Force a clean rerun so we don't depend on this run's local variables
#     st.rerun()

# # ---------------------------------
# # With sheets confirmed, proceed
# # ---------------------------------
# sheet1 = st.session_state.selected_sheet1
# sheet2 = st.session_state.selected_sheet2

# with st.expander("📄 Current sheet selection", expanded=True):
#     st.markdown(f"- **Penetration trends**: `{sheet1}`")
#     st.markdown(f"- **Value drivers**: `{sheet2}`")
#     change_cols = st.columns([1, 2, 2, 2])
#     with change_cols[0]:
#         if st.button("🔄 Change sheets"):
#             st.session_state.sheets_confirmed = False
#             st.session_state.brand_owner = None
#             st.rerun()

# # ----------------------------
# # Verify layout for penetration
# # ----------------------------
# try:
#     _ = pd.read_excel(
#         fresh_io(),
#         sheet_name=sheet1,
#         skiprows=1,
#         header=[0, 1, 2, 3],
#         nrows=1,
#         engine="openpyxl",
#     )
# except ValueError as ve:
#     st.error(f"Selected penetration trends sheet '{sheet1}' appears to have an unexpected layout: {ve}")
#     st.stop()

# # -----------------------------------
# # Initial pipeline: top opportunities
# # -----------------------------------
# try:
#     df_final = preprocessing_excel(fresh_io(), sheet1)
#     df_top = identify_opportunities(df_final, tangible_threshold, growing_threshold)
# except Exception as e:
#     st.error(f"Error while preprocessing the penetration sheet: {e}")
#     st.stop()

# if "BRAND OWNER" not in df_top.columns:
#     st.error("The input does not contain a 'BRAND OWNER' column after preprocessing. Please check your data.")
#     st.stop()

# unique_brand_owners = sorted(df_top['BRAND OWNER'].dropna().unique().tolist())
# if not unique_brand_owners:
#     st.warning("No brand owners detected in the selected sheets. Please verify your workbook content.")
#     st.stop()

# # -----------------------------
# # Brand owner selection (sticky)
# # -----------------------------
# # Set default only once (fix: use real ampersand)
# if (st.session_state.brand_owner is None) or (st.session_state.brand_owner not in unique_brand_owners):
#     if "PROCTER & GAMBLE" in unique_brand_owners:
#         st.session_state.brand_owner = "PROCTER & GAMBLE"
#     else:
#         st.session_state.brand_owner = unique_brand_owners[0]

# st.write("### Select Brand Owner for Risk Calculation")
# brand_owner = st.selectbox(
#     "Brand owner",
#     options=unique_brand_owners,
#     key="brand_owner",  # persists selection across reruns
#     help="Select a brand owner from the list. You can type to search."
# )

# # -----------------------------
# # Continue the pipeline
# # -----------------------------
# try:
#     df2 = preprocessing_value_drivers(fresh_io(), sheet2)
#     df_merged = merging_data(df_top, df2)
#     df_priority = calculate_value_driver_contributions(df_merged)
#     df_risks = identify_risks(df_top, brand_owner)
# except Exception as e:
#     st.error(f"Error during processing: {e}")
#     st.stop()

# st.success("✅ Processing complete!")

# # ---------------------------------
# # Prepare Excel downloads in memory
# # ---------------------------------
# buf1 = io.BytesIO()
# with pd.ExcelWriter(buf1, engine="xlsxwriter") as writer:
#     df_priority.to_excel(writer, index=False, sheet_name="Priority Brands")
# buf1.seek(0)

# buf2 = io.BytesIO()
# with pd.ExcelWriter(buf2, engine="xlsxwriter") as writer:
#     df_risks.to_excel(writer, index=False, sheet_name="Risks")
# buf2.seek(0)

# # ---------------------------------
# # Download section (styled header)
# # ---------------------------------
# st.markdown(
#     """
#     <style>
#     .download-header {
#         background: linear-gradient(135deg, #1f7a3c 0%, #2d9e52 100%);
#         padding: 20px;
#         border-radius: 10px;
#         margin: 10px 0;
#     }
#     .download-header h2 {
#         color: white;
#         text-align: center;
#         margin: 0 0 15px 0;
#     }
#     </style>
#     <div class="download-header">
#         <h2>📊 Download Results</h2>
#     </div>
#     """,
#     unsafe_allow_html=True
# )

# col_dl1, col_dl2 = st.columns(2)
# with col_dl1:
#     st.download_button(
#         label="📥 Priority Brands",
#         data=buf1,
#         file_name=f"{brand_owner}_priority_brands.xlsx",
#         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         use_container_width=True,
#         help="Download the priority brands analysis workbook"
#     )
# with col_dl2:
#     st.download_button(
#         label="📥 Risk Analysis",
#         data=buf2,
#         file_name=f"{brand_owner}_risks.xlsx",
#         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         use_container_width=True,
#         help="Download the risk analysis workbook"
#     )

# st.divider()
# st.write("### 📈 Priority Brands sample")
# st.dataframe(df_priority.head(), use_container_width=True)
# st.write("### ⚠️ Risks sample")
# st.dataframe(df_risks.head(), use_container_width=True)


# streamlit_app.py
import streamlit as st
import pandas as pd
import io
import hashlib
import os

from code_52_26_wks import (
    preprocessing_excel,
    identify_opportunities,
    preprocessing_value_drivers,
    merging_data,
    calculate_value_driver_contributions,
    identify_risks,
)

st.set_page_config(page_title="P&G Growth Opportunities & Risks", layout="wide")

# -------------------------
# Session-state bootstrapping
# -------------------------
if "uploaded_file_hash" not in st.session_state:
    st.session_state.uploaded_file_hash = None
if "sheets_confirmed" not in st.session_state:
    st.session_state.sheets_confirmed = False
if "selected_sheet1" not in st.session_state:
    st.session_state.selected_sheet1 = None
if "selected_sheet2" not in st.session_state:
    st.session_state.selected_sheet2 = None
if "brand_owner" not in st.session_state:
    st.session_state.brand_owner = None

# -------------------------
# Minimal structural CSS (theme-safe)
# -------------------------
st.markdown(
    """
    <style>
      .niq-header {
        padding: 6px 0 12px 0;
        border-bottom: 1px solid rgba(128,128,128,0.25);
        margin-bottom: 8px;
      }
      .niq-app-title {
        font-weight: 800;
        font-size: 1.6rem;
        margin: 0 0 2px 0;
      }
      .niq-app-subtitle {
        font-size: 1.05rem;
        margin: 2px 0 0 0;
        opacity: 0.95;
      }
      .niq-app-copy {
        margin-top: 6px;
        opacity: 0.85;
        font-size: 0.95rem;
      }
      .right-align {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        height: 100%;
      }
      .tight-section { margin-top: 0.25rem; margin-bottom: 0.5rem; }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------
# NIQ Header (logo left, text right)
# -------------------------
with st.container():
    st.markdown('<div class="niq-header">', unsafe_allow_html=True)
    col_logo, col_titles = st.columns([1, 9])
    with col_logo:
        # Provide your logo file (placed next to this app file).
        # The code tries multiple typical filenames.
        logo_candidates = [
            "NIQ-logo.png",
            "NIQ-logo-bright-blue-web.png",
            "NIQ.png",
        ]
        logo_path = next((p for p in logo_candidates if os.path.exists(p)), None)
        if logo_path:
            st.image(logo_path, width=110)
        else:
            st.markdown("**NIQ**")  # fallback text if the logo file isn't found
    with col_titles:
        # Title and subtitle (theme colors are respected)
        st.markdown('<div class="niq-app-title">CS AI CoE</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="niq-app-subtitle">Growth Opportunities & Risks Analysis</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="niq-app-copy">Upload your raw Excel workbook and get instant insights on priority brands and risk assessment</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# -------------------------
# File upload & configuration
# -------------------------
uploaded_file = st.file_uploader("Choose Excel file", type=["xls", "xlsx"])

st.markdown("### ⚙️ Configuration")
col1, col2 = st.columns(2)
with col1:
    tangible_threshold = st.number_input(
        "Tangible threshold (Latest 52 Wks > ?)",
        min_value=0.0,
        value=2.0
    )
with col2:
    growing_threshold = st.number_input(
        "Growing penetration threshold (Latest 26 vs YA > ?)",
        min_value=0.0,
        value=0.2
    )

# ---------------------------------
# If a file has been uploaded...
# ---------------------------------
if uploaded_file is None:
    st.info("Please upload an Excel file to begin.")
    st.stop()

# Cache file bytes once; create fresh BytesIO for every read
file_bytes = uploaded_file.getvalue()
def fresh_io():
    return io.BytesIO(file_bytes)

# Hash to detect new file and reset state when file changes
file_hash = hashlib.md5(file_bytes).hexdigest()[:8]
if st.session_state.uploaded_file_hash != file_hash:
    # New file: reset sheet + brand owner choices
    st.session_state.uploaded_file_hash = file_hash
    st.session_state.sheets_confirmed = False
    st.session_state.selected_sheet1 = None
    st.session_state.selected_sheet2 = None
    st.session_state.brand_owner = None

# Get sheets from file
try:
    xls = pd.ExcelFile(fresh_io())
    raw_sheets = xls.sheet_names
except Exception as e:
    st.error(f"Couldn't open the Excel file: {e}")
    st.stop()

# ---------------------------------
# Sheet selection gate (one-time)
# ---------------------------------
if not st.session_state.sheets_confirmed:
    st.markdown("### 📄 Sheet Selection")

    # Smart detection
    default_sheet1_idx = 0  # Because [None] is index 0 in the selection below
    default_sheet2_idx = 0
    detected_sheet1 = None
    detected_sheet2 = None

    for idx, sheet_name in enumerate(raw_sheets):
        sheet_name_upper = sheet_name.upper()
        if "PENETRATION" in sheet_name_upper and detected_sheet1 is None:
            default_sheet1_idx = idx + 1  # shift by 1 for the [None] option
            detected_sheet1 = sheet_name
        if "KPI" in sheet_name_upper and detected_sheet2 is None:
            default_sheet2_idx = idx + 1
            detected_sheet2 = sheet_name

    if detected_sheet1:
        st.success(f"✓ Auto-detected Penetration sheet: **{detected_sheet1}**")
    if detected_sheet2:
        st.success(f"✓ Auto-detected KPI sheet: **{detected_sheet2}**")

    # Use content hash as part of form key to reset on actual file change
    form_key = f"sheet_form_{file_hash}"

    with st.form(key=form_key):
        sheet1_choice = st.selectbox(
            "Select the sheet for penetration trends",
            options=[None] + raw_sheets,
            index=default_sheet1_idx,
            format_func=lambda x: "" if x is None else x,
        )
        sheet2_choice = st.selectbox(
            "Select the sheet for value drivers",
            options=[None] + raw_sheets,
            index=default_sheet2_idx,
            format_func=lambda x: "" if x is None else x,
        )
        submit_sheets = st.form_submit_button("Load sheets")

    if not submit_sheets:
        st.info("Please choose the two sheets above and press **Load sheets** to start.")
        st.stop()

    if sheet1_choice is None or sheet2_choice is None:
        st.error("❌ Please select both sheets before submitting.")
        st.stop()

    if sheet1_choice == sheet2_choice:
        st.error("❌ Penetration and value driver sheets must be different.")
        st.stop()

    # Persist and continue
    st.session_state.selected_sheet1 = sheet1_choice
    st.session_state.selected_sheet2 = sheet2_choice
    st.session_state.sheets_confirmed = True
    # Force a clean rerun so we don't depend on this run's local variables
    st.rerun()

# ---------------------------------
# With sheets confirmed, proceed
# ---------------------------------
sheet1 = st.session_state.selected_sheet1
sheet2 = st.session_state.selected_sheet2

with st.expander("📄 Current sheet selection", expanded=True):
    st.markdown(f"- **Penetration trends**: `{sheet1}`")
    st.markdown(f"- **Value drivers**: `{sheet2}`")
    change_cols = st.columns([1, 2, 2, 2])
    with change_cols[0]:
        if st.button("🔄 Change sheets"):
            st.session_state.sheets_confirmed = False
            st.session_state.brand_owner = None
            st.rerun()

# ----------------------------
# Verify layout for penetration
# ----------------------------
try:
    _ = pd.read_excel(
        fresh_io(),
        sheet_name=sheet1,
        skiprows=1,
        header=[0, 1, 2, 3],
        nrows=1,
        engine="openpyxl",
    )
except ValueError as ve:
    st.error(f"Selected penetration trends sheet '{sheet1}' appears to have an unexpected layout: {ve}")
    st.stop()

# -----------------------------------
# Initial pipeline: top opportunities
# -----------------------------------
try:
    df_final = preprocessing_excel(fresh_io(), sheet1)
    df_top = identify_opportunities(df_final, tangible_threshold, growing_threshold)
except Exception as e:
    st.error(f"Error while preprocessing the penetration sheet: {e}")
    st.stop()

if "BRAND OWNER" not in df_top.columns:
    st.error("The input does not contain a 'BRAND OWNER' column after preprocessing. Please check your data.")
    st.stop()

unique_brand_owners = sorted(df_top['BRAND OWNER'].dropna().unique().tolist())
if not unique_brand_owners:
    st.warning("No brand owners detected in the selected sheets. Please verify your workbook content.")
    st.stop()

# -----------------------------
# Brand owner selection (sticky)
# -----------------------------
# Set default only once (use real ampersand)
if (st.session_state.brand_owner is None) or (st.session_state.brand_owner not in unique_brand_owners):
    if "PROCTER & GAMBLE" in unique_brand_owners:
        st.session_state.brand_owner = "PROCTER & GAMBLE"
    else:
        st.session_state.brand_owner = unique_brand_owners[0]

st.write("### Select Brand Owner for Risk Calculation")
brand_owner = st.selectbox(
    "Brand owner",
    options=unique_brand_owners,
    key="brand_owner",  # persists selection across reruns
    help="Select a brand owner from the list. You can type to search."
)

# -----------------------------
# Continue the pipeline
# -----------------------------
try:
    df2 = preprocessing_value_drivers(fresh_io(), sheet2)
    df_merged = merging_data(df_top, df2)
    df_priority = calculate_value_driver_contributions(df_merged)
    df_risks = identify_risks(df_top, brand_owner)
except Exception as e:
    st.error(f"Error during processing: {e}")
    st.stop()

st.success("✅ Processing complete!")

# ---------------------------------
# Prepare Excel downloads in memory
# ---------------------------------
buf1 = io.BytesIO()
with pd.ExcelWriter(buf1, engine="xlsxwriter") as writer:
    df_priority.to_excel(writer, index=False, sheet_name="Priority Brands")
buf1.seek(0)

buf2 = io.BytesIO()
with pd.ExcelWriter(buf2, engine="xlsxwriter") as writer:
    df_risks.to_excel(writer, index=False, sheet_name="Risks")
buf2.seek(0)

# ---------------------------------
# Priority Brands section (heading left + download right)
# ---------------------------------
pb_left, pb_right = st.columns([4, 1])
with pb_left:
    st.markdown("### 📈 Priority Brands sample")
with pb_right:
    st.markdown('<div class="right-align">', unsafe_allow_html=True)
    st.download_button(
        label="📥 Download",
        data=buf1,
        file_name=f"{brand_owner}_priority_brands.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        help="Download the priority brands analysis workbook"
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.dataframe(df_priority.head(), use_container_width=True)

st.markdown("---")

# ---------------------------------
# Risks section (heading left + download right)
# ---------------------------------
rk_left, rk_right = st.columns([4, 1])
with rk_left:
    st.markdown("### 🚨 Risks sample")
with rk_right:
    st.markdown('<div class="right-align">', unsafe_allow_html=True)
    st.download_button(
        label="📥 Download",
        data=buf2,
        file_name=f"{brand_owner}_risks.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        help="Download the risk analysis workbook"
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.dataframe(df_risks.head(), use_container_width=True)

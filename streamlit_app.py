import streamlit as st
import pandas as pd
import io
import hashlib

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
# Custom styling for the app
# -------------------------
st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(135deg, #1f7a3c 0%, #2d9e52 100%);
        padding: 25px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: #e8f5e9;
        margin: 10px 0 0 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="main-header">
        <h1>Growth Opportunities & Risks Analysis</h1>
        <p>Upload your raw Excel workbook and get instant insights on priority brands and risk assessment</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

uploaded_file = st.file_uploader("Choose Excel file", type=["xls", "xlsx"])

st.markdown("### ⚙️ Configuration")
# allow the user to override some thresholds
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
sheet1 = None
sheet2 = None

if uploaded_file is not None:
    try:
        # Cache file bytes once; create fresh BytesIO for every read
        file_bytes = uploaded_file.getvalue()
        def fresh_io():
            return io.BytesIO(file_bytes)

        # Build ExcelFile from a fresh buffer
        xls = pd.ExcelFile(fresh_io())
        raw_sheets = xls.sheet_names

        st.markdown("### 📄 Sheet Selection")

        # Smart detection: find sheets matching keywords (case-insensitive)
        default_sheet1_idx = 0  # +1 is for None below, so 0 means "None"
        default_sheet2_idx = 0
        detected_sheet1 = None
        detected_sheet2 = None

        for idx, sheet_name in enumerate(raw_sheets):
            sheet_name_upper = sheet_name.upper()
            if "PENETRATION" in sheet_name_upper and detected_sheet1 is None:
                default_sheet1_idx = idx + 1  # because [None] is index 0
                detected_sheet1 = sheet_name
            if "KPI" in sheet_name_upper and detected_sheet2 is None:
                default_sheet2_idx = idx + 1
                detected_sheet2 = sheet_name

        if detected_sheet1:
            st.success(f"✓ Auto-detected Penetration sheet: **{detected_sheet1}**")
        if detected_sheet2:
            st.success(f"✓ Auto-detected KPI sheet: **{detected_sheet2}**")

        # Use content hash as part of form key to reset on actual file change
        file_hash = hashlib.md5(file_bytes).hexdigest()[:8]
        form_key = f"sheet_form_{file_hash}"

        with st.form(key=form_key):
            sheet1 = st.selectbox(
                "Select the sheet for penetration trends",
                options=[None] + raw_sheets,
                index=default_sheet1_idx,
                format_func=lambda x: "" if x is None else x,
            )
            sheet2 = st.selectbox(
                "Select the sheet for value drivers",
                options=[None] + raw_sheets,
                index=default_sheet2_idx,
                format_func=lambda x: "" if x is None else x,
            )
            submit_sheets = st.form_submit_button("Load sheets")
    except Exception as e:
        submit_sheets = False
        st.error(f"Couldn't open the Excel file: {e}")

    if not submit_sheets:
        st.info("Please choose the two sheets above and press **Load sheets** to start.")
    elif sheet1 is None or sheet2 is None:
        st.error("❌ Please select both sheets before submitting.")
    elif sheet1 == sheet2:
        st.error("❌ Penetration and value driver sheets must be different.")
    else:
        # User has confirmed which sheets to load; perform all processing here
        try:
            # ----------------------------
            # Verify layout for penetration
            # ----------------------------
            try:
                # Always read from a fresh buffer
                _ = pd.read_excel(
                    fresh_io(),
                    sheet_name=sheet1,
                    skiprows=1,
                    header=[0, 1, 2, 3],
                    nrows=1
                )
            except ValueError as ve:
                st.error(f"Selected penetration trends sheet '{sheet1}' appears to have an unexpected layout: {ve}")
                raise

            # -----------------------------------
            # Initial pipeline: top opportunities
            # -----------------------------------
            df_final = preprocessing_excel(fresh_io(), sheet1)
            df_top = identify_opportunities(df_final, tangible_threshold, growing_threshold)

            # Extract unique brand owners for dropdown
            if "BRAND OWNER" not in df_top.columns:
                st.error("The input does not contain a 'BRAND OWNER' column after preprocessing. Please check your data.")
                st.stop()

            unique_brand_owners = sorted(df_top['BRAND OWNER'].dropna().unique().tolist())

            if not unique_brand_owners:
                st.warning("No brand owners detected in the selected sheets. Please verify your workbook content.")
                st.stop()

            # Default to P&G if available (use real ampersand)
            default_index = 0
            if 'PROCTER & GAMBLE' in unique_brand_owners:
                default_index = unique_brand_owners.index('PROCTER & GAMBLE')

            st.write("### Select Brand Owner for Risk Calculation")
            brand_owner = st.selectbox(
                "Brand owner",
                options=unique_brand_owners,
                index=default_index,
                help="Select a brand owner from the list. You can type to search."
            )

            # -----------------------------
            # Continue the pipeline
            # -----------------------------
            df2 = preprocessing_value_drivers(fresh_io(), sheet2)
            df_merged = merging_data(df_top, df2)
            df_priority = calculate_value_driver_contributions(df_merged)
            df_risks = identify_risks(df_top, brand_owner)

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
            # Download section (styled header)
            # ---------------------------------
            st.markdown(
                """
                <style>
                .download-header {
                    background: linear-gradient(135deg, #1f7a3c 0%, #2d9e52 100%);
                    padding: 20px;
                    border-radius: 10px;
                    margin: 10px 0;
                }
                .download-header h2 {
                    color: white;
                    text-align: center;
                    margin: 0 0 15px 0;
                }
                </style>
                <div class="download-header">
                    <h2>📊 Download Results</h2>
                </div>
                """,
                unsafe_allow_html=True
            )

            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    label="📥 Priority Brands",
                    data=buf1,
                    file_name=f"{brand_owner}_priority_brands.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    help="Download the priority brands analysis workbook"
                )
            with col_dl2:
                st.download_button(
                    label="📥 Risk Analysis",
                    data=buf2,
                    file_name=f"{brand_owner}_risks.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    help="Download the risk analysis workbook"
                )

            st.divider()
            st.write("### 📈 Priority Brands sample")
            st.dataframe(df_priority.head(), use_container_width=True)
            st.write("### ⚠️ Risks sample")
            st.dataframe(df_risks.head(), use_container_width=True)

        except Exception as e:
            # If the error is due to header mismatch, guide user instead of dumping traceback
            msg = str(e)
            if "header index" in msg.lower():
                st.error("The selected sheet does not have the expected multi-row header layout. Please choose a different sheet.")
            else:
                st.error(f"Error during processing: {e}")
                st.exception(e)
else:
    st.info("Please upload an Excel file to begin.")
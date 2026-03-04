import streamlit as st
import pandas as pd
import io

from code_52_26_wks import (
    preprocessing_excel,
    identify_top_opportunities,
    preprocessing_value_drivers,
    merging_data,
    calculate_value_driver_contributions,
    identify_risks,
)

st.set_page_config(page_title="P&G Growth Opportunities & Risks", layout="wide")

# custom styling for the app
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
        <h1> Growth Opportunities & Risks Analysis</h1>
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
    tangible_threshold = st.number_input("Tangible threshold (Penetration in Latest 52 Wks > ?)", min_value=0.0, value=2.0)
with col2:
    growing_threshold = st.number_input("Growing penetration threshold (Penetration change inLatest 26 vs YA > ?)", min_value=0.0, value=0.2)

if uploaded_file is not None:
    try:
        # run initial pipeline to identify unique brand owners
        sheet1 = "Penetration Trends Template"
        sheet2 = "KPIs - EU5 template"

        # preprocessing accepts file-like, pandas handles it
        df_final = preprocessing_excel(uploaded_file, sheet1)
        df_top = identify_top_opportunities(df_final, tangible_threshold, growing_threshold)
        
        # extract unique brand owners for dropdown
        unique_brand_owners = sorted(df_top['BRAND OWNER'].unique().tolist())
        
        # display brand owner selectbox with search capability (searchable dropdown)
        st.write("### Select Brand Owner for Risk Calculation")
        brand_owner = st.selectbox(
            "Brand owner",
            options=unique_brand_owners,
            index=0 if unique_brand_owners else None,
            help="Select a brand owner from the list. You can type to search."
        )
        
        # continue with remaining pipeline using selected brand owner
        df2 = preprocessing_value_drivers(uploaded_file, sheet2)
        df_merged = merging_data(df_top, df2)
        df_priority = calculate_value_driver_contributions(df_merged)
        df_risks = identify_risks(df_top, brand_owner)

        st.success("✅ Processing complete!")
        
        # prepare download buffers
        buf1 = io.BytesIO()
        with pd.ExcelWriter(buf1, engine="xlsxwriter") as writer:
            df_priority.to_excel(writer, index=False)
        buf1.seek(0)

        buf2 = io.BytesIO()
        with pd.ExcelWriter(buf2, engine="xlsxwriter") as writer:
            df_risks.to_excel(writer, index=False)
        buf2.seek(0)

        # display prominent download buttons in green
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

    except Exception:
        st.error("Please check your file format and upload again")
else:
    st.info("Please upload an Excel file to begin.")

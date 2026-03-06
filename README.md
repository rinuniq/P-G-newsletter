# P&G Growth Opportunities & Risks Analysis

## Project Overview

This project analyzes Procter & Gamble (P&G) brand performance data to identify growth opportunities and potential risks. It processes penetration trends and value driver data from raw Excel workbooks and generates automated insights on brand priorities and risk assessments.

The application provides an interactive **Streamlit dashboard** that allows users to:
- Upload raw Excel data
- Configure analysis thresholds
- Identify top opportunity brands
- Analyze value drivers (Buyers, Occasions per Buyer, Value per Occasion)
- Detect risk patterns (Growth Deceleration, Decline Acceleration)
- Download detailed reports

---

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Streamlit Application
```bash
streamlit run streamlit_app.py
```

The application will open in your browser at `http://localhost:8501`

### Step 3: Run Standalone Script (Optional)
For batch processing without the dashboard:
```bash
python main.py
```

---

## Architecture & Core Functions

### 1. **preprocessing_excel(file_path, sheet_name)**
**Purpose:** Transforms raw Excel penetration data into a normalized analytical format.

**Input:**
- `file_path`: Path to the Excel workbook
- `sheet_name`: Sheet name (typically "Penetration Trends Template")

**Processing Steps:**
1. Reads multi-level header Excel file (4 header rows)
2. Drops the 2nd header level (country names in header1 are preserved in header0)
3. Renames metrics with "vs YA" suffix if the period contains "YA" (Year-Ago comparison)
4. Flattens multi-level columns and melts data from wide to long format
5. Pivots metrics back to columns for easier analysis

**Output DataFrame Columns:**
- `row_id`: Unique row identifier
- `People`: Target demographic
- `Currency`: Transaction currency
- `Total Panel`: Size of the analysis panel
- `Total Outlets`: Number of retail outlets
- `CATEGORY`: Product category
- `BRAND OWNER`: Brand ownership company
- `BRAND`: Brand name
- `country`: Geographic market
- `Latest 26 Wks`: Penetration % in last 26 weeks
- `Latest 26 vs YA`: YoY change % (26 weeks)
- `Latest 52 Wks`: Penetration % in last 52 weeks
- `Latest 52 vs YA`: YoY change % (52 weeks)

---

### 2. **identify_top_opportunities(df_final, tangible_threshold, growing_threshold)**
**Purpose:** Classifies brands based on multiple penetration criteria to identify top opportunities.

> **UI changes (2026 update)**: Sheet selection resides inside a Streamlit **form**, so uploading a file does **not** trigger any processing. Two dropdowns appear **blank initially** (no sheet selected) and will populate once the file is loaded; the user must actively pick each sheet. Only after clicking **Load sheets** does the workbook get read. This eliminates stray errors on upload. If the chosen penetration‑trends sheet lacks the expected four‑row header layout, a friendly prompt instructs you to pick a different sheet rather than showing a traceback. The brand‑owner dropdown still defaults to "PROCTER & GAMBLE" when that name appears in the list.

**Parameters:**
- `df_final`: Output from preprocessing_excel
- `tangible_threshold`: Minimum penetration % to be considered "Tangible" (default: 2.0%)
- `growing_threshold`: Minimum YoY growth % to be considered "Growing" (default: 0.2%)

**Classification Logic:**

#### a) **Tangible Brands**
- **Condition:** `Latest 52 Wks > tangible_threshold`
- **Meaning:** Brand has meaningful market presence (>2% penetration in past 52 weeks)
- **Rationale:** Filters out negligible brands with minimal market impact

#### b) **Growing Penetration**
- **Condition:** `Latest 26 vs YA > growing_threshold`
- **Meaning:** Brand is expanding in recent period vs. same period last year (>0.2% growth)
- **Rationale:** Identifies brands with positive momentum in latest performance window

#### c) **Accelerating Penetration**
- **Condition:** `Latest 26 vs YA > Latest 52 vs YA`
- **Meaning:** Growth rate in recent 26 weeks exceeds the 52-week average growth
- **Rationale:** Shows brands gaining speed/momentum rather than decelerating

#### d) **Top Opportunity**
- **Condition:** Tangible Brands = 'Yes' **AND** Growing Penetration = 'Yes' **AND** Accelerating Penetration = 'Yes'
- **Meaning:** Brand is established, growing, and accelerating—highest priority for investment
- **Result:** Only these brands proceed to value driver analysis

**Output:** DataFrame with 4 new classification columns added

---

### 3. **preprocessing_value_drivers(file_path, sheet_name)**
**Purpose:** Processes value driver decomposition data showing what's driving sales changes.

**Input:**
- `file_path`: Excel workbook path
- `sheet_name`: Sheet name (typically "KPIs - EU5 template")

**Processing:**
1. Reads multi-level header data (2 header rows)
2. Extracts time period from header0 (e.g., "Latest 52 Wks-EU5" → "Latest 52 Wks")
3. Combines metric name + time period for clarity
4. Preserves first 8 columns as metadata (Countries, Category, Brand, etc.)
5. Normalizes missing values to 0

**Output DataFrame Contains:**
- Metadata: Countries, CATEGORY, BRAND, BRAND OWNER, etc.
- Value Drivers for **Latest 52 Wks** and **Latest 26 Wks**:
  - `Value vs YA (Abs Change)`: Total value change vs prior year
  - `Value due to Buyers YA`: Change attributable to buyer count changes
  - `Value due to Occasions per Buyer YA`: Change attributable to purchase frequency
  - `Value due to Value per Occasion YA`: Change attributable to price/mix shifts

---

### 4. **merging_data(df_top_opportunities, df2_processed)**
**Purpose:** Combines brand classification with value driver metrics.

**Merge Strategy:**
1. Filters `df_top_opportunities` to keep only rows where `Top Opportunity = 'Yes'`
2. Selects key value driver columns from `df2_processed`
3. Performs LEFT JOIN matching on: `[country, CATEGORY, BRAND]`
4. Drops redundant country column

**Output:** Merged DataFrame with both penetration classifications and value drivers

---

### 5. **calculate_value_driver_contributions(df_merged)**
**Purpose:** Calculates what percentage each value driver contributed to total value change.

**Calculations:**
For each time period (52 weeks & 26 weeks):
```
Contribution % = (Value due to Component) / (Total Value change) × 100
```

**Three Components:**
1. **Buyer Contribution %**: % of value change from new/returning customers
2. **Occasions Contribution %**: % of value change from increased purchase frequency
3. **Value per Occasion Contribution %**: % of value change from price/mix improvements

**Sorting:** Results sorted by Latest 26 Weeks value change (descending) for priority ranking

**Final Output Columns:**
- Core metrics: Currency, Category, Brand Owner, Brand, Country, Penetration %
- Change metrics: Latest 26/52 weeks YoY changes
- Classifications: Tangible, Growing, Accelerating, Top Opportunity flags
- Value drivers (52 & 26 weeks): Absolute changes per component
- Contributions (52 & 26 weeks): % allocation per component
- **Total 26 columns for comprehensive analysis**

---

### 6. **identify_risks(df_top_opportunities, brand_owner)**
**Purpose:** Detects concerning growth patterns in selected brand owner's portfolio.

**Parameters:**
- `df_top_opportunities`: Classification data from Step 2
- `brand_owner`: Target brand owner (e.g., "PROCTER & GAMBLE")

**Risk Detection Logic:**

Only brands matching the specified `brand_owner` are evaluated:

#### a) **Growth Deceleration**
- **Condition:** 
  - `Latest 52 vs YA > 0` (was growing over 52 weeks)
  - **AND** `Latest 26 vs YA < Latest 52 vs YA` (26-week growth is worse than 52-week average)
- **Meaning:** Brand's growth momentum is slowing down
- **Example:** Was growing 2% (52wks avg) but only 0.5% (26wks recent)

#### b) **Decline Acceleration**
- **Condition:** 
  - `Latest 52 vs YA < 0` (was declining over 52 weeks)
  - **AND** `Latest 26 vs YA < Latest 52 vs YA` (decline is getting worse)
- **Meaning:** Brand's negative trend is accelerating
- **Example:** Was declining -1% (52wks avg) but -3% (26wks recent)

#### c) **No Risk**
- All other brands marked as "No risk"
- Other brand owners' brands always marked as "No risk"

**Output:** Filtered DataFrame with only at-risk brands for the selected brand owner

---

## Data Flow Diagram

```
Raw Excel File
      ↓
┌─────────────────────────────────────┐
│ Sheet 1: Penetration Trends         │
└────────────┬────────────────────────┘
             ↓
    preprocessing_excel()
             ↓
      df_final (normalized)
             ↓
identify_top_opportunities() ← [Tangible > 2%, Growing > 0.2%, Accelerating]
             ↓
      df_top_opportunities
        ↙ (Top Opportunity=Yes)  ↘ (all brands)
       ↓
  merging_data() ← Sheet 2: Value Drivers
       ↓
   df_merged
       ↓
calculate_value_driver_contributions()  →  Priority Brands Output
       ↓
identify_risks(brand_owner)  →  Risks Output
```

---

## Configuration Parameters

### In Streamlit App (Interactive)
Users can adjust thresholds on the fly:
- **Tangible threshold**: Minimum Latest 52 Wks penetration % (default: 2.0)
- **Growing penetration threshold**: Minimum Latest 26 vs YA growth % (default: 0.2)

### In main.py (Batch Mode)
```python
tangible_threshold = 2.0      # Brands must have >2% penetration
growing_threshold = 0.2       # Brands must be growing >0.2% YoY
brand_owner = 'PROCTER & GAMBLE'
```

---

## File Structure

```
P-G-newsletter/
├── streamlit_app.py           # Interactive Streamlit dashboard
├── code_52_26_wks.py          # Core analysis functions library
├── main.py                    # Batch processing script
├── requirements.txt           # Python dependencies
├── code_52_26_wks.ipynb       # Jupyter notebook for development
├── code_pqr.ipynb             # Related analysis notebook
├── .gitignore                 # Git configuration
└── README.md                  # This file
```

---

## Usage Examples

### Example 1: Interactive Dashboard
```bash
streamlit run streamlit_app.py
```
1. Upload Excel file via file uploader
2. Adjust thresholds if needed
3. Select brand owner from dropdown
4. Download "Priority Brands" and "Risks" reports

### Example 2: Batch Processing
Edit `main.py` with your parameters:
```python
file_path = "your_data.xlsx"
brand_owner = "PROCTER & GAMBLE"
tangible_threshold = 2.0
growing_threshold = 0.2
```
Then run:
```bash
python main.py
```

### Example 3: Custom Analysis
```python
from code_52_26_wks import *

# Load and preprocess
df = preprocessing_excel("data.xlsx", "Penetration Trends Template")

# Identify opportunities with custom thresholds
df_opp = identify_top_opportunities(df, tangible_threshold=1.5, growing_threshold=0.1)

# Print summary
print(df_opp[['BRAND', 'Tangible Brands', 'Growing Penetration', 'Top Opportunity']])
```

---

## Output Files

### Priority Brands Excel Report
Columns include:
- Brand identification (Owner, Category, Brand, Country)
- Penetration metrics (Latest 26/52 weeks and YoY changes)
- Classifications (Tangible, Growing, Accelerating, Top Opportunity)
- Value driver breakdown (52 & 26 week periods)
- Contribution % by component (Buyers, Occasions, Value per Occasion)

**Sorted by:** Latest 26 weeks value change (highest first)

**Use Case:** Strategic prioritization of growth initiatives

### Risk Analysis Excel Report
Columns include:
- Brand identification (Owner, Category, Brand, Country)
- Penetration metrics (Latest 26/52 weeks and YoY changes)
- Classifications
- Risk flag: "Growth Deceleration", "Decline Acceleration", or "No"

**Filtered to:** Brands with identified risks only

**Use Case:** Risk mitigation and portfolio management

---

## Thresholds & Conditions Summary

| Metric | Condition | Default | Purpose |
|--------|-----------|---------|---------|
| **Tangible Brands** | Latest 52 Wks > Threshold | 2.0% | Minimum viable market presence |
| **Growing Penetration** | Latest 26 vs YA > Threshold | 0.2% | Positive recent momentum |
| **Accelerating Penetration** | L26 Growth > L52 Growth | N/A | Growth rate improvement |
| **Top Opportunity** | All 3 above conditions met | N/A | Premium prioritization |
| **Growth Deceleration** | L52 > 0 & L26 < L52 | N/A | Slowing growth risk |
| **Decline Acceleration** | L52 < 0 & L26 < L52 | N/A | Worsening decline risk |

---

## Dependencies

- **pandas** (2.3.3): Data manipulation and analysis
- **openpyxl** (3.1.5): Excel file I/O
- **streamlit** (1.55.0): Interactive web dashboard
- **xlsxwriter** (3.2.9): Excel report generation
- **numpy** (2.4.2): Numerical operations

---

## Troubleshooting

**Issue:** "Sheet not found" error
- **Solution:** Verify sheet names match exactly: "Penetration Trends Template" and "KPIs - EU5 template"

**Issue:** Brand owner not showing in dropdown
- **Solution:** Ensure at least one brand meets Top Opportunity criteria (all 3 checks pass)

**Issue:** Value driver columns empty
- **Solution:** Check that brands exist in both sheet1 (Penetration) and sheet2 (KPIs) data

**Issue:** Division by zero in contribution calculations
- **Solution:** Only occurs for brands with zero total value change; filtered automatically

---

## Future Enhancements

- [ ] Support for additional brand owners through multi-select
- [ ] Custom chart visualizations in Streamlit
- [ ] Time-series trend analysis
- [ ] Benchmark comparisons across categories
- [ ] Automated alerts for critical risks
- [ ] Historical data tracking and variance analysis

---

## Notes

- All thresholds are configurable and user-adjustable
- Analysis filters to top opportunities before detailed value driver analysis
- Risk assessment is always brand-owner specific for targeted insights
- Year-ago (YA) comparisons provide seasonality-adjusted metrics
- Contribution percentages may exceed 100% if multiple drivers offset losses

---

## Support & Questions

For questions about the analysis methodology or to report issues, refer to the function docstrings in [code_52_26_wks.py](code_52_26_wks.py).

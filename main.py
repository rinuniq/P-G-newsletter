from code_52_26_wks import *

file_path=r"C:\Users\rdi5001\OneDrive - NIQ\Desktop\P&G\P-G-newsletter\MAIN_Penetration and Value Drivers Template_raw data for Divyaa & Rinu v2.xlsx"
sheet1="Penetration Trends Template"
sheet2="KPIs - EU5 template"

tangible_threshold,growing_threshold=2,0.2
brand_owner='PROCTER & GAMBLE'

df_final=preprocessing_excel(file_path, sheet1)

df_opportunities=identify_opportunities(df_final, tangible_threshold, growing_threshold)
# brand_owners=df_top_opportunities['BRAND OWNER'].unique().tolist()
df_value_drivers=preprocessing_value_drivers(file_path, sheet2)

df_merged=merging_data(df_opportunities, df_value_drivers)

df_priority=calculate_value_driver_contributions(df_merged)

df_risks=identify_risks(df_opportunities,brand_owner)

df_priority.to_excel(f'{brand_owner}_priority_brands.xlsx', index=False)
df_risks.to_excel(f'{brand_owner}_risks.xlsx', index=False)
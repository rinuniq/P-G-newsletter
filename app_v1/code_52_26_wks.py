import pandas as pd

def preprocessing_excel(file_path, sheet1):
    df1 = pd.read_excel(
    file_path,
    sheet_name=sheet1,
   skiprows=1,
    header=[0,1,2,3],
    engine='openpyxl')

    # Replace Unnamed columns in the 3rd header level (level index 2) after column 7 with 'Total Europe'
    # Replace Unnamed columns in the 3rd header level (level index 2) after column 7 with 'Total Europe'
    cols = list(df1.columns)
    new_cols = []
    for i, col in enumerate(cols):
        col_list = list(col)
        if i >= 7 and len(col_list) > 2 and isinstance(col_list[2], str) and col_list[2].startswith('Unnamed'):
            col_list[2] = col_list[1]
        new_cols.append(tuple(col_list))
    df1.columns = pd.MultiIndex.from_tuples(new_cols)
    
    # Create a new view of df1 keeping header levels 1, 3, and 4 (human numbering)
    # -> which are 0-based levels 0, 2, and 3 in pandas
    df1_trimmed = df1.copy()
    df1_trimmed.columns = df1_trimmed.columns.droplevel(1)

    # alternative transformation using melt, treating first 7 columns as metadata
    # use df_base from earlier steps

    # determine metadata and data columns by position
    metadata_cols = list(df1_trimmed.columns[:7])
    # we'll slice by position for data rather than by labels
    data_cols_raw = list(df1_trimmed.columns[7:])
    
    # print("Metadata cols:", metadata_cols)
    # print("First few raw data cols:", data_cols_raw[:5])
    

    
    renamed_data = []
    for col in data_cols_raw:
        col=list(col)
        if "YA" in str(col[0]).upper():
            col[2] = f"{col[2]} vs YA"
    
        renamed_data.append((col[1], col[2]))
    
    # slice the data portion of df_base and then rename its columns
    df_data = df1_trimmed.iloc[:, 7:].copy()
    df_data.columns = pd.MultiIndex.from_tuples(renamed_data)
    # print(df_data.columns)
    
    # also extract df_meta for later use
    df_meta = df1_trimmed.iloc[:, :7].copy()

    
    meta_display_names = [col[-1] for col in metadata_cols]
    # print("Meta display names:", meta_display_names)
    
    # flatten df_data columns
    flat_cols = [f"{c0}|||{c1}" for c0, c1 in renamed_data]
    df_flat = df_data.copy()
    df_flat.columns = flat_cols
    
    # add meta columns to flat using LAST LEVEL names
    for col, disp in zip(metadata_cols, meta_display_names):
        df_flat[f"meta|||{disp}"] = df_meta[col]


    df_flat['row_id'] = df_flat.index

    
    # melt on metric columns
    id_vars = ['row_id'] + [f"meta|||{disp}" for disp in meta_display_names]
    df_melt = df_flat.melt(id_vars=id_vars, var_name='combined', value_name='value')

    # split combined into country and metric
    split_cols = df_melt['combined'].str.split('\\|\\|\\|',expand=True)

    df_melt['country'] = split_cols[0]
    df_melt['metric'] = split_cols[1]
    
    # pivot back
    df_final = df_melt.pivot_table(
        index=id_vars + ['country'],
        columns='metric',
        values='value',
        aggfunc='first'
    ).reset_index()

    # clean metadata column names: remove the "meta|||" prefix using the same display names
    for disp in meta_display_names:
        df_final = df_final.rename(columns={f"meta|||{disp}": disp})
        # print("Transformed final shape:", df_final.shape)
        df_final.columns=['row_id', 'People', 'Currency', 'Total Panel', 'Total Outlets',
        'CATEGORY', 'BRAND OWNER', 'BRAND', 'country',
        'Latest 26 Wks', 'Latest 26 vs YA',
        'Latest 52 Wks', 'Latest 52 vs YA']
        df_final = df_final.fillna(0)

    return df_final

def identify_opportunities(df_final,tangible_threshold,growing_threshold):
    df_opportunities = df_final.copy()
    df_opportunities['Tangible Brands'] = df_opportunities['Latest 52 Wks'].apply(lambda x: 'Yes' if x > tangible_threshold else 'No')
    df_opportunities['Growing Penetration'] = df_opportunities['Latest 26 vs YA'].apply(lambda x: 'Yes' if x > growing_threshold else 'No')
    df_opportunities['Accelerating Penetration'] = (df_opportunities['Latest 26 vs YA'] > df_opportunities['Latest 52 vs YA']).apply(lambda x: 'Yes' if x else 'No')
    df_opportunities['Top Opportunity'] = (
    (df_opportunities['Tangible Brands'] == 'Yes') & 
    (df_opportunities['Growing Penetration'] == 'Yes') & 
    (df_opportunities['Accelerating Penetration'] == 'Yes')).apply(lambda x: 'Yes' if x else 'No')

    return df_opportunities

def preprocessing_value_drivers(file_path, sheet2):
    df2 = pd.read_excel(
    file_path,
    sheet_name=sheet2,
    skiprows=1,
    header=[0,1],
    engine='openpyxl')

    # Process df2: Keep MultiIndex to properly extract header0 and header1
    df2_copy = df2.copy()

    # Identify metadata columns (first 8 by position)
    metadata_cols = list(df2_copy.columns[:8])
    data_cols = list(df2_copy.columns[8:])



    # Process the data columns: extract header0 (time period) + header1 (metric)
    renamed_cols = []

    for col in data_cols:
        h0, h1 = col[0], col[1]  # col is a tuple (header0, header1)
        
        # Split header0 at '-' and take the first part
        time_period = h0.split('-')[0].strip()
        
        # Combine metric + time period
        new_col = f"{h1} {time_period}"
        renamed_cols.append(new_col)


    # Create new dataframe with renamed columns
    df2_meta = df2_copy.iloc[:, :8].copy()
    df2_data = df2_copy.iloc[:, 8:].copy()

    # Flatten column names to single level
    df2_meta.columns = [col[1] for col in df2_meta.columns]
    df2_data.columns = renamed_cols

    # Concatenate metadata and data
    df2_processed = pd.concat([df2_meta, df2_data], axis=1)
    df2_processed=df2_processed.fillna(0)

    return df2_processed

def merging_data(df_opportunities, df2_processed):
   # merge procedure between Top_Oppurtunity (from df_final) and df2_processed
    # assume df_final and df2_processed exist
    df_top_opportunities=df_opportunities[df_opportunities['Top Opportunity']=='Yes']

    # select necessary columns from df2_processed
    right_cols = [
        'Countries','CATEGORY','BRAND',
        'Value vs YA (Abs Change) Latest 52 Wks',
        'Value due to Buyers YA Latest 52 Wks',
        'Value due to Occasions per Buyer YA Latest 52 Wks',
        'Value due to Value per Occasion YA Latest 52 Wks',
        'Value vs YA (Abs Change) Latest 26 Wks',
        'Value due to Buyers YA Latest 26 Wks',
        'Value due to Occasions per Buyer YA Latest 26 Wks',
        'Value due to Value per Occasion YA Latest 26 Wks',
    ]

    # build small right table
    df2_small = df2_processed[right_cols].copy()

    df_merged = df_top_opportunities.merge(
        df2_small,
        left_on=['country','CATEGORY','BRAND'],
        right_on=['Countries','CATEGORY','BRAND'],
        how='left'
    )

    # drop auxiliary column
    if 'Countries' in df_merged.columns:
        df_merged = df_merged.drop(columns=['Countries'])

    return df_merged

def calculate_value_driver_contributions(df_merged):
   # calculate contribution percentages for each value component and week
    weeks = ['52','26']
    components = ['Value due to Buyers YA','Value due to Occasions per Buyer YA','Value due to Value per Occasion YA']

    for wk in weeks:
        denom_col = f'Value vs YA (Abs Change) Latest {wk} Wks'
        for comp in components:
            num_col = f'{comp} Latest {wk} Wks'
            new_col = f'Contribution {comp} Latest {wk} Wks'
            df_merged[new_col] = df_merged[num_col] / df_merged[denom_col] * 100

    # Sort df_merged by Value vs YA (Abs Change) Latest 13 Wks in descending order
    df_priority = df_merged.sort_values(
        by='Value vs YA (Abs Change) Latest 26 Wks',
        ascending=False
    ).reset_index(drop=True)

    df_priority_final=df_priority[[ 'Currency', 
       'CATEGORY', 'BRAND OWNER', 'BRAND', 'country', 'Latest 26 Wks',
       'Latest 26 vs YA', 'Latest 52 Wks', 'Latest 52 vs YA',
       'Tangible Brands', 'Growing Penetration', 'Accelerating Penetration',
       'Top Opportunity', 'Value vs YA (Abs Change) Latest 52 Wks',
       'Value due to Buyers YA Latest 52 Wks',
       'Value due to Occasions per Buyer YA Latest 52 Wks',
       'Value due to Value per Occasion YA Latest 52 Wks',
       'Value vs YA (Abs Change) Latest 26 Wks',
       'Value due to Buyers YA Latest 26 Wks',
       'Value due to Occasions per Buyer YA Latest 26 Wks',
       'Value due to Value per Occasion YA Latest 26 Wks',
       'Contribution Value due to Buyers YA Latest 52 Wks',
       'Contribution Value due to Occasions per Buyer YA Latest 52 Wks',
       'Contribution Value due to Value per Occasion YA Latest 52 Wks',
       'Contribution Value due to Buyers YA Latest 26 Wks',
       'Contribution Value due to Occasions per Buyer YA Latest 26 Wks',
       'Contribution Value due to Value per Occasion YA Latest 26 Wks']]

    return df_priority_final

def identify_risks(df_opportunities,brand_owner):

    df_risks=df_opportunities.copy()
    # define a helper that applies the two rules only for P&G brands
    # brand_owner is now a parameter with a default value; the result
    # column name is constructed separately so we can reference it easily.
    def calculate_pg_risk(row,brand_owner):
        if row['BRAND OWNER'] != brand_owner:
            return 'No'                       # keep others as “No”
        l52 = row['Latest 52 vs YA']
        l26 = row['Latest 26 vs YA']

        # declining‑growth
        if l52 > 0 and l26 < l52 :
            return 'Growth Deceleration'
        # declining‑deceleration
        if l52 < 0 and l26 < l52:
            return 'Decline Acceleration'
        return 'No'

    # assign the column
    colname = f"{brand_owner} risk"
    # use a lambda to pass the brand_owner argument to the function
    # (alternatively the default value in calculate_pg_risk could be used)
    df_risks[colname] = df_risks.apply(lambda r: calculate_pg_risk(r, brand_owner), axis=1)
    df_risks1=df_risks[df_risks[colname]!='No']
    # print('Risk columns:', df_risks1.columns)
    df_risks_final=df_risks1[[ 'Currency','CATEGORY', 'BRAND OWNER', 'BRAND', 'country', 'Latest 26 Wks','Latest 26 vs YA', 'Latest 52 Wks', 'Latest 52 vs YA','Tangible Brands', 'Growing Penetration', 'Accelerating Penetration', 'Top Opportunity', f'{brand_owner} risk']]
    return df_risks_final

    




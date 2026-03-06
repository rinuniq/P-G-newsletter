AIM:

To identify top opportunities and momentum risks for a given brand.

THEORY:

1) TANGIBLE BRANDS: Brands that have pentration greater than 2pp in the latest 52 weeks are considered tangible.

2) GROWING PENETRATION: Brands that have penetration change greater than 0.2 pp in the latest 26 weeks VS YA are considered to have growing penetration.

3) ACCELERATING PENETRATION: Brands that have penetration change in latest 26 weeks greater than that of latest 52 weeks are considered to have accelerating penetration.

4) TOP OPPORTUNITY: Brands that satisfy the above three conditions(tangible, growing & accelerating penetration) are considered to be top opportunities.

5) VALUE DRIVERS: Value can be driven by:
  - Buyers
  - Occasion per buyer
  - Value per occasion
  Summing all gives value

6) MOMENTUM RISKS FOR THE GIVEN BRAND:
- growth deceleration examples would be: 
  L52w 6%, L26w 3%
  L52w 3%, L26w -3%
  L52w 3%, L26w -3%
  The penetration change in latest 52 weeks is positive and it is becoming less positive over time.
- decline acceleration examples would be:
  L52w -3%, L26w -4%
  L52w -3%, L26w -2%
  L52w -3%, L26w +1%
  The penetration change in latest 52 weeks is negative and is becoming more negative over time.


PROCEDURE:

1) Load the data that contains penetration trends in sheet1 and value drivers in sheet2.
2) Preprocess the penetration trends data.
3) Add new columns in the penetration trends data and flag tangible brands, growing penetration and accelerating penetration. If all three are met, flag it as a top opportunity.
4) Preprocess the second sheet that contains information about value drivers. Create columns that contain the contribution percentage of each value driver.
5) Merge sheet1 that contains only top opportunities to sheet 2. This will give the value contribution of the brands under each category and country flagged as top opportunities. Sort it by Value so that brands that contribute the most are prioritised.
6) Now, go to the sheet1 data that contains both top and not top opportunities and flag momentum risks based on the theory. Filter only the rows were the given brand is found to have risks like growth deceleration/decline acceleration.
7) We have two resulting dataframes:
 - df_priority: has only the brands flagged as top opportunities and their corresponding contribution to value.
 - df_risks: has only the the category and country of the given brand which are found to have momentum risks.

 APP:

 We have also developed an app that allows the user to upload the main data and get the resulting files(done using streamlit).
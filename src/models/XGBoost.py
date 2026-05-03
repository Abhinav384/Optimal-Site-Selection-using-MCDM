import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split

# 1. Load your data
df = pd.read_csv('/content/sample_data/land_surface_temperature.csv')
df['Date'] = pd.to_datetime(df['Date'])

# 2. Get the ACTUAL unique locations from your data
unique_locs = df[['Latitude', 'Longitude']].drop_duplicates()

# 3. Create the complete date range
all_dates = pd.date_range(df['Date'].min(), df['Date'].max(), freq='D')

# 4. Create the expected 3,100 rows (100 locs × 31 days)
# First create a DataFrame with all location-date combinations
complete_df = pd.DataFrame(
    [(lat, lon, date) for (lat, lon) in unique_locs.itertuples(index=False) 
                     for date in all_dates],
    columns=['Latitude', 'Longitude', 'Date']
)

# 5. Merge with original data to preserve existing values
final_df = pd.merge(
    complete_df,
    df,
    on=['Latitude', 'Longitude', 'Date'],
    how='left'
)

print(f"Final DataFrame has {len(final_df)} rows")  # Should be exactly 3,100

# Add temporal features
final_df['day_of_year'] = final_df['Date'].dt.dayofyear
final_df['month'] = final_df['Date'].dt.month

# Identify missing values
missing_mask = final_df['LST'].isna()

if missing_mask.sum() == 0:
    print("No missing dates found - data is complete")
else:
    print(f"Found {missing_mask.sum()} missing values to predict")
    
    # Prepare data for modeling
    from xgboost import XGBRegressor
    
    # Split into known and unknown
    known = final_df[~missing_mask]
    unknown = final_df[missing_mask]
    
    # Train model
    model = XGBRegressor(
      n_estimators=200,
      learning_rate=0.05,
      max_depth=6,
      subsample=0.8,
      colsample_bytree=0.8,
      random_state=42
    )

    model.fit(
        known[['Latitude', 'Longitude', 'day_of_year', 'month']],
        known['LST']
    )
    
    # Make predictions
    final_df.loc[missing_mask, 'LST'] = model.predict(
        unknown[['Latitude', 'Longitude', 'day_of_year', 'month']]
    )
    
    # Save results
    final_df.to_csv('lst_predicted_data.csv', index=False)
    print(f"Saved {len(final_df)} rows (100 locations × 31 days)")
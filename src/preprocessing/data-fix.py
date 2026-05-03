import pandas as pd
from datetime import timedelta

# Load only the first 9000 rows
df = pd.read_csv("data/Amritsar_May2024_Hourly_GHI_Fixed.csv", nrows=9000)

# Ensure required columns exist
required_columns = ['City', 'Coordinate', 'date', 'hour', 'surface_solar_radiation_downwards']
if not all(col in df.columns for col in required_columns):
    raise ValueError("CSV must contain columns: " + ", ".join(required_columns))

# Convert 'date' to datetime and 'hour' to int
df['date'] = pd.to_datetime(df['date'])
df['hour'] = df['hour'].astype(int)

# Shift the hour by -1 (rolling hour 0 to 23 of previous day)
def shift_hour(row):
    if row['hour'] == 0:
        return pd.Series({
            'date': row['date'] - timedelta(days=1),
            'hour': 23
        })
    else:
        return pd.Series({
            'date': row['date'],
            'hour': row['hour'] - 1
        })

df[['date', 'hour']] = df.apply(shift_hour, axis=1)

# Sort and save
df = df.sort_values(by=['Coordinate', 'date', 'hour']).reset_index(drop=True)
df.to_csv("Amritsar_May2024_Hourly_GHI_FIXED_9000.csv", index=False)

print("✅ Fixed 9000-row subset saved to 'Amritsar_May2024_Hourly_GHI_FIXED_9000.csv'")

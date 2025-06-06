import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Path to pickle file
file_path = 'C:/Users/lucak/OneDrive/Desktop/Aviatik Studium/Semester 6/BA/LSZH_MAY_SEP_df_movements.pkl'

# Read df_movements
df_movements = pd.read_pickle(file_path)

# filter for takeoffs
df_movements = df_movements.query('isTakeoff and takeoffRunway != "14" and stand_area != "unkown"')

# Fix parkin positions
df_movements['parking_position'] = df_movements['parking_position'].fillna(df_movements['stand_area'])
df_movements['parking_position'] = df_movements['parking_position'].replace({
    'AB Courtyard': 'AB',
    'A North': 'A',
    'B South': 'B'
})
df_movements['parking_position_gen'] = df_movements['parking_position'].apply(
    lambda x: x[:2] if x.startswith('AB') else x[0]
)

# Widebody-list
WB = ['A332', 'A333', 'A343', 'A346', 'A35K', 'A359', 'A388', 'B744', 'B763', 'B764',
      'B772', 'B773', 'B77L', 'B77W', 'B788', 'B789', 'B78X', 'B748']

# Time preparation
df_movements['startTaxi'] = pd.to_datetime(df_movements['startTaxi'], utc=True).dt.tz_localize(None)
df_movements['date'] = df_movements['startTaxi'].dt.date
df_movements['hour'] = df_movements['startTaxi'].dt.hour

# Filter: WB + Gate E + RWY 16/28/32
df_wb = df_movements[
    (df_movements['typecode'].isin(WB)) &
    (df_movements['parking_position_gen'] == 'E') &
    (df_movements['takeoffRunway'].isin(['16', '28', '32']))
]

# Table for hours of the day
hourly_counts_per_day = (
    df_wb.groupby(['date', 'hour'])
    .size()
    .unstack(fill_value=0)
    .reindex(columns=range(24), fill_value=0)
)

# Calculate statistics
average_hourly = hourly_counts_per_day.mean(axis=0)
percentile_95_hourly = hourly_counts_per_day.quantile(0.95, axis=0)
max_hourly = hourly_counts_per_day.max(axis=0)
print(percentile_95_hourly)
# Plot
plt.figure(figsize=(10, 6))
plt.plot(average_hourly.index, average_hourly.values, label='Mittelwert', color='orange', linewidth=2)
plt.plot(percentile_95_hourly.index, percentile_95_hourly.values, label='95%-Perzentil', color='blue', linestyle='--', linewidth=2)
plt.plot(max_hourly.index, max_hourly.values, label='Maximum', color='red', linestyle=':', linewidth=2)

plt.title('Taxi-Starts Widebodies (WB) – Gate E → RWY 16/28/32')
plt.xlabel('Hour of the day (UTC+2)')
plt.ylabel('Number of taxi-out')
plt.xticks(range(0, 24))
plt.grid(True, axis='y')
plt.legend()
plt.tight_layout()
plt.show()

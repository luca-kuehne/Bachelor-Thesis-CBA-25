import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Path to pickle file
file_path = 'C:/Users/lucak/OneDrive/Desktop/Aviatik Studium/Semester 6/BA/LSZH_MAY_SEP_df_movements.pkl'

# Read df_movements
df_movements = pd.read_pickle(file_path)

# Filter for takeoffs and clean data
df_movements = df_movements.query('isTakeoff and takeoffRunway != "14" and stand_area != "unkown"')

# Fix parking position
df_movements['parking_position'] = df_movements['parking_position'].fillna(df_movements['stand_area'])
df_movements['parking_position'] = df_movements['parking_position'].replace({
    'AB Courtyard': 'AB',
    'A North': 'A',
    'B South': 'B'
})
df_movements['parking_position_gen'] = df_movements['parking_position'].apply(
    lambda x: x[:2] if x.startswith('AB') else x[0]
)

# Narrowbody list
NB = ['A220', 'A318', 'A319', 'A320', 'A20N', 'A321', 'A21N', 'BCS1', 'BCS3',
      'B733', 'B734', 'B735', 'B737', 'B738', 'B739', 'B73J', 'B38M', 'B39M',
      'B752', 'B753', 'E75L', 'E75S', 'E190', 'E195', 'E290', 'E295']

# Time preparation
df_movements['startTaxi'] = pd.to_datetime(df_movements['startTaxi'], utc=True).dt.tz_localize(None)
df_movements['date'] = df_movements['startTaxi'].dt.date
df_movements['hour'] = df_movements['startTaxi'].dt.hour

# Filter for NB aircraft with combined requirements:
# (A/AB/B/C/D → RWY 28) OR (E → RWY 16, 28, 32)
df_nb = df_movements[
    (df_movements['typecode'].isin(NB)) & (
        ((df_movements['parking_position_gen'].isin(['A', 'AB', 'B', 'C', 'D'])) &
         (df_movements['takeoffRunway'] == '28')) |
        ((df_movements['parking_position_gen'] == 'E') &
         (df_movements['takeoffRunway'].isin(['16', '28', '32'])))
    )
]

# Table: hours over day
hourly_counts_per_day_nb = (
    df_nb.groupby(['date', 'hour'])
    .size()
    .unstack(fill_value=0)
    .reindex(columns=range(24), fill_value=0)
)

# calculation of statistics
average_hourly_nb = hourly_counts_per_day_nb.mean(axis=0)
percentile_95_hourly_nb = hourly_counts_per_day_nb.quantile(0.95, axis=0)
max_hourly_nb = hourly_counts_per_day_nb.max(axis=0)

print(percentile_95_hourly_nb)

# Plot: max, 95th percentile, mean
plt.figure(figsize=(10, 6))
plt.plot(average_hourly_nb.index, average_hourly_nb.values, label='Mittelwert', color='black', linestyle='--', linewidth=2)
plt.plot(percentile_95_hourly_nb.index, percentile_95_hourly_nb.values, label='95%-Perzentil', color='red', linewidth=2)
plt.plot(max_hourly_nb.index, max_hourly_nb.values, label='Maximum', color='grey', linestyle='--', linewidth=2)

plt.title('Taxi-out Narrowbodies (NB)\nA/AB/B/C/D → RWY 28, E → RWY 16/28/32')
plt.xlabel('Hours of the day (UTC+2)')
plt.ylabel('Numbers of taxi-out')
plt.xticks(range(0, 24))
plt.grid(True, axis='y')
plt.legend()
plt.tight_layout()
plt.show()

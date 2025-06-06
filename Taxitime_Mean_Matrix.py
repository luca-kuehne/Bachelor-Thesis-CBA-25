import pandas as pd
import numpy as np

# Path to pickle file
file_path = 'C:/Users/lucak/OneDrive/Desktop/Aviatik Studium/Semester 6/BA/LSZH_MAY_SEP_df_movements.pkl'

# Read df_movements (df_movements is the output of agps_proc.ipynb)
df_movements = pd.read_pickle(file_path)
 
# Filter for takeoff only
df_movements = df_movements.query('isTakeoff', engine='python')
 
# Get rid of departures classified as runway 14 -> These are outliers (no aircraft take off on runway 14 at ZRH in real life)
df_movements = df_movements.query('takeoffRunway!="14"')
 
# Get rid of unknown stand areas (written as "unkown" in the data)
df_movements = df_movements.query('stand_area!="unkown"')
 
# If there is no value in parking_position, take the value from stand_area and just take the short information (e.g. "A" instead of "A North")
df_movements['parking_position'] = df_movements['parking_position'].fillna(df_movements['stand_area'])
df_movements['parking_position'] = df_movements['parking_position'].replace('AB Courtyard', 'AB')
df_movements['parking_position'] = df_movements['parking_position'].replace('A North', 'A')
df_movements['parking_position'] = df_movements['parking_position'].replace('B South', 'B')
 
df_movements.head()
# Fix the parking position
df_movements['parking_position_gen'] = df_movements['parking_position'].apply(
    lambda x: x[:2] if x.startswith('AB') else x[0]
)

# List with typecodes of narrowbodies and widebodies
NB = ['A220', 'A318', 'A319', 'A320', 'A20N', 'A321', 'A21N', 'BCS1', 'BCS3',
      'B733', 'B734', 'B735', 'B737', 'B738', 'B739', 'B73J', 'B38M', 'B39M',
      'B752', 'B753', 'E75L', 'E75S', 'E190', 'E195', 'E290', 'E295']
WB = ['A332', 'A333', 'A343', 'A346', 'A35K', 'A359', 'A388', 'B744', 'B763', 'B764',
      'B772', 'B773', 'B77L', 'B77W', 'B788', 'B789', 'B78X', 'B748']

# Initialize matrices with zeros and dtype object for mixed types
AC_NB = np.zeros((7, 15), dtype='object')
AC_WB = np.zeros((7, 15), dtype='object')

# Initialize dictionaries to store sum of times and counts for averaging
time_count_NB = {key: [0, 0] for key in np.ndindex(AC_NB.shape)}
time_count_WB = {key: [0, 0] for key in np.ndindex(AC_WB.shape)}

# Set headers for matrices
labels = ["########", "A", "AB", "B", "C", "D", "E", "F", "G", "H", "I", "P", "T", "V", "W"]
runways = ["########", "10", "14", "16", "28", "32", "34"]
AC_NB[0, :] = labels
AC_NB[:, 0] = runways
AC_WB[0, :] = labels
AC_WB[:, 0] = runways

# Maps for column and row indexes
parking_to_index = {key: i for i, key in enumerate(labels[1:])}
runway_to_index = {key: i for i, key in enumerate(runways[1:])}

# Count movements and store taxi durations
for index, row in df_movements.iterrows():
    parking_pos = row['parking_position_gen']
    runway = row['takeoffRunway']
    typecode = row['typecode']
    if parking_pos in parking_to_index and runway in runway_to_index:
        parking_index = parking_to_index[parking_pos] + 1  # +1 due to label column
        runway_index = runway_to_index[runway] + 1  # +1 due to label row
        
        if typecode in WB:
            time_count = time_count_WB[(runway_index, parking_index)]
        elif typecode in NB:
            time_count = time_count_NB[(runway_index, parking_index)]
        else:
            continue  # Skip if typecode not in WB or NB
        
        taxi_duration = row['taxiDuration'].total_seconds()  # Convert Timedelta to seconds
        time_count[0] += taxi_duration
        time_count[1] += 1

# Calculate average taxi times and store in matrices
for key, value in time_count_NB.items():
    if value[1] > 0:
        AC_NB[key] = round(value[0] / value[1], 2)
for key, value in time_count_WB.items():
    if value[1] > 0:
        AC_WB[key] = round(value[0] / value[1], 2)

# Convert matrices to pandas DataFrames
df_AC_NB = pd.DataFrame(AC_NB[1:, 1:], index=runways[1:], columns=labels[1:])
df_AC_WB = pd.DataFrame(AC_WB[1:, 1:], index=runways[1:], columns=labels[1:])

# Display the results
print("Narrow Body Movements Table:")
print(df_AC_NB)
print("\nWide Body Movements Table:")
print(df_AC_WB)

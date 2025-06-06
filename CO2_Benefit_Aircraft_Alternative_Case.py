import pandas as pd
import numpy as np
from openap.emission import Emission

# Aircraft info
AIRCRAFT_INFO = {
    "BCS1": {"max_pax": 110, "engine": "PW1524G", "n_engines": 2},
    "BCS3": {"max_pax": 130, "engine": "PW1524G", "n_engines": 2},
    "E290": {"max_pax": 120, "engine": "PW1919G", "n_engines": 2},
    "E295": {"max_pax": 132, "engine": "PW1921G", "n_engines": 2},
    "A35K": {"max_pax": 350, "engine": "trent xwb-97", "n_engines": 2},
    "CRJ9": {"max_pax": 90, "engine": "CF34-8C5", "n_engines": 2},
    "B77L": {"max_pax": 320, "engine": "Trent 892", "n_engines": 2},
    "B78X": {"max_pax": 300, "engine": "Trent 1000-K2", "n_engines": 2},
    "B733": {"max_pax": 130, "engine": "CFM56-3B", "n_engines": 2},
    "B735": {"max_pax": 108, "engine": "CFM56-3B", "n_engines": 2},
    "B736": {"max_pax": 108, "engine": "CFM56-7B", "n_engines": 2},
    "B753": {"max_pax": 243, "engine": "PW2037", "n_engines": 2},
    "B762": {"max_pax": 210, "engine": "CF6-80C2B7F", "n_engines": 2},
    "B764": {"max_pax": 245, "engine": "CF6-80C2B8F", "n_engines": 2},
    "CRJ2": {"max_pax": 50, "engine": "CF34", "n_engines": 2},
    "CRJ7": {"max_pax": 70, "engine": "CF34-8C1", "n_engines": 2},
    "CRJX": {"max_pax": 104, "engine": "CF34-8C5A1", "n_engines": 2},
    "E75S": {"max_pax": 78, "engine": "CF34-8E6", "n_engines": 2},
}

# File path
file_path = 'C:/Users/lucak/OneDrive/Desktop/Aviatik Studium/Semester 6/BA/LSZH_MAY_SEP_df_movements.pkl'
df_movements = pd.read_pickle(file_path)

# Data cleaning and prep
df_movements = df_movements.query('isTakeoff', engine='python')
df_movements = df_movements.query('takeoffRunway!="14"')
df_movements = df_movements.query('stand_area!="unkown"')
df_movements['parking_position'] = df_movements['parking_position'].fillna(df_movements['stand_area'])
df_movements['parking_position'] = df_movements['parking_position'].replace({
    'AB Courtyard': 'AB', 'A North': 'A', 'B South': 'B'
})
df_movements['parking_position_gen'] = df_movements['parking_position'].apply(
    lambda x: x[:2] if x.startswith('AB') else x[0]
)

# Aircraft classification
NB = ['A220', 'A318', 'A319', 'A320', 'A20N', 'A321', 'A21N', 'BCS1', 'BCS3',
      'B733', 'B734', 'B735', 'B737', 'B738', 'B739', 'B73J', 'B38M', 'B39M',
      'B752', 'B753', 'E75L', 'E75S', 'E190', 'E195', 'E290', 'E295']
WB = ['A332', 'A333', 'A343', 'A346', 'A35K', 'A359', 'A388', 'B744', 'B763', 'B764',
      'B772', 'B773', 'B77L', 'B77W', 'B788', 'B789', 'B78X', 'B748']

# Matrices
AC_NB = np.zeros((7, 15), dtype='object')
AC_WB = np.zeros((7, 15), dtype='object')
labels = ["########", "A", "AB", "B", "C", "D", "E", "F", "G", "H", "I", "P", "T", "V", "W"]
runways = ["########", "10", "14", "16", "28", "32", "34"]
AC_NB[0, :] = labels
AC_NB[:, 0] = runways
AC_WB[0, :] = labels
AC_WB[:, 0] = runways
parking_to_index = {key: i for i, key in enumerate(labels[1:])}
runway_to_index = {key: i for i, key in enumerate(runways[1:])}

# Loop through movements
for _, row in df_movements.iterrows():
    parking_pos = row['parking_position_gen']
    runway = row['takeoffRunway']
    typecode = row['typecode']
    engIdleFF = row['engIdleFF']
    lineupTime = row['lineupTime']
    startTaxi = row['startTaxi']
    pushback = row['isPushback']
    startPush = row['startPushback']
    ffapu = row['APUhighFF']

    if parking_pos not in parking_to_index or runway not in runway_to_index:
        continue

    parking_index = parking_to_index[parking_pos] + 1
    runway_index = runway_to_index[runway] + 1
    matrix = AC_WB if typecode in WB else AC_NB if typecode in NB else None
    if matrix is None:
        continue

    # Taxi time minus 4 minutes warmup
    t = (lineupTime - startPush).total_seconds() - 240 if pushback == "WAHR" else (lineupTime - startTaxi).total_seconds() - 240
    if t < 0:
        continue
    # Emission object based on engine if available
    if typecode in AIRCRAFT_INFO:
        engine_type = AIRCRAFT_INFO[typecode]["engine"]
        nEngines = AIRCRAFT_INFO[typecode]["n_engines"]
        emission = Emission(ac="a320", engine=engine_type) # it needs a type, but the type will not be used
    else:
        nEngines = row['nEngines']
        emission = Emission(ac=typecode.lower())

    ff_rate_c = nEngines * engIdleFF
    co2_rate = emission.co2(ff_rate_c)
    CO2 = co2_rate * t / 1000  # g → kg

    # Add CO2 emissions to matrix
    matrix[runway_index, parking_index] = CO2 if matrix[runway_index, parking_index] == 0 else matrix[runway_index, parking_index] + CO2

    # APU emissions
    apu_fuel_burn_rate = ffapu / 3600  # kg/s
    apu_fuel_burned = apu_fuel_burn_rate * t
    apu_co2_emission = apu_fuel_burned * 3.16  # kg CO₂/kg fuel

    matrix[runway_index, parking_index] -= apu_co2_emission

# Convert to DataFrames
df_AC_NB = pd.DataFrame(AC_NB[1:, 1:], index=runways[1:], columns=labels[1:])
df_AC_WB = pd.DataFrame(AC_WB[1:, 1:], index=runways[1:], columns=labels[1:])

# Output
print("Narrow Body Movements Table:")
print(df_AC_NB)
print("\nWide Body Movements Table:")
print(df_AC_WB)

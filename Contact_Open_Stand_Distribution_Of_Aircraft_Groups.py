import pandas as pd

# Read data
# Read df_movements (df_movements is the output of agps_proc.ipynb)
df_movements = pd.read_pickle('LSZH_MAY_SEP_df_movements.pkl')

# Filter for takeoffs only
df_movements = df_movements.query('isTakeoff', engine='python')

# Remove departures classified as runway 14 -> these are outliers (no aircraft takes off on runway 14 at ZRH in real life)
df_movements = df_movements.query('takeoffRunway!="14"')

# Remove entries with unknown stand areas (written as "unkown" in the data)
df_movements = df_movements.query('stand_area!="unkown"')

# If there is no value in parking_position, take the value from stand_area
df_movements['parking_position'] = df_movements['parking_position'].fillna(df_movements['stand_area'])
df_movements['parking_position'] = df_movements['parking_position'].replace('AB Courtyard', 'AB')
df_movements['parking_position'] = df_movements['parking_position'].replace('A North', 'A')
df_movements['parking_position'] = df_movements['parking_position'].replace('B South', 'B')

# Extract the first letter for the general parking position, except for "AB", keep both letters
df_movements['parking_position_gen'] = df_movements['parking_position'].apply(
    lambda x: x[:2] if x.startswith('AB') else x[0])

# List of type codes for narrowbody aircraft
# No regional aircraft like CRJ, ATR or Dash 8 in this list
NB = ['A220', 'A318', 'A319', 'A320', 'A20N', 'A321', 'A21N', 'BCS1', 'BCS3',
      'B733','B734', 'B735','B737', 'B738', 'B739', 'B73J', 'B38M',
      'B39M', 'B752', 'B753', 'E75L', 'E75S','E190', 'E195', 'E290','E295']

# List of type codes for widebody aircraft
WB = ['A332', 'A333', 'A343', 'A346', 'A35K','A359', 'A388', 'B744','B763', 'B764',
      'B772', 'B773', 'B77L', 'B77W', 'B788', 'B789', 'B78X', 'B748']

# Filter only NB and WB flights
df_movements = df_movements[df_movements['typecode'].isin(NB + WB)]

# Modify the "isPushback" column and set it to True if "parking_position" is in ["AB", "A", "B", "E", "P"]
df_movements['isPushback'] = df_movements.apply(
    lambda row: True if row['parking_position_gen'] in ['AB', 'A', 'B', 'E', 'P'] else False, axis=1)

# Determine the share of pushback and non-pushback flights relative to the total number of flights for NB and WB
total_flights = len(df_movements)
narrowbody_flights = len(df_movements[df_movements['typecode'].isin(NB)])
widebody_flights = len(df_movements[df_movements['typecode'].isin(WB)])
narrowbody_percentage = (narrowbody_flights / total_flights)
widebody_percentage = (widebody_flights / total_flights)
total_flights_percentage = (narrowbody_percentage + widebody_percentage)

# Determine the share of pushback and non-pushback flights relative to total flights for NB and WB
# Narrowbody
pushback_flights_nb = len(df_movements[(df_movements['typecode'].isin(NB)) & (df_movements['isPushback'] == True)])
non_pushback_flights_nb = len(df_movements[(df_movements['typecode'].isin(NB)) & (df_movements['isPushback'] == False)])

pushback_percentage_nb = (pushback_flights_nb / narrowbody_flights) if narrowbody_flights > 0 else 0
non_pushback_percentage_nb = (non_pushback_flights_nb / narrowbody_flights) if narrowbody_flights > 0 else 0

# Widebody
pushback_flights_wb = len(df_movements[(df_movements['typecode'].isin(WB)) & (df_movements['isPushback'] == True)])
non_pushback_flights_wb = len(df_movements[(df_movements['typecode'].isin(WB)) & (df_movements['isPushback'] == False)])

pushback_percentage_wb = (pushback_flights_wb / widebody_flights) if widebody_flights > 0 else 0
non_pushback_percentage_wb = (non_pushback_flights_wb / widebody_flights) if widebody_flights > 0 else 0

# Calculate the total share of pushback and non-pushback flights
# considering the proportions of narrowbody and widebody aircraft
total_pushback_flights_percentage = (pushback_percentage_nb * narrowbody_percentage) + (pushback_percentage_wb * widebody_percentage)
total_non_pushback_flights_percentage = (non_pushback_percentage_nb * narrowbody_percentage) + (non_pushback_percentage_wb * widebody_percentage)

# Create a table with the results
results = pd.DataFrame({
    'Aircraft Group': ['Narrowbody', 'Widebody', 'Total'],
    'Group share': [round(narrowbody_percentage * 100, 2), round(widebody_percentage * 100, 2), total_flights_percentage * 100],
    'Contact stand operations': [round(pushback_percentage_nb * 100, 2), round(pushback_percentage_wb * 100, 2), round(total_pushback_flights_percentage * 100, 2)],
    'Open stand operations': [round(non_pushback_percentage_nb * 100, 2), round(non_pushback_percentage_wb * 100, 2), round(total_non_pushback_flights_percentage * 100, 2)],
})
print(results)
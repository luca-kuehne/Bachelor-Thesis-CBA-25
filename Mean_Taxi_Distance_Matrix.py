import pandas as pd

# Read data
# Read df_movements (df_movements is the output of agps_proc.ipynb)
df_movements = pd.read_pickle('LSZH_MAY_SEP_df_movements.pkl')

# Extract the first letter for the general parking position, except for "AB" where both letters are used
df_movements['parking_position_gen'] = df_movements['parking_position'].apply(
    lambda x: x[:2] if x.startswith('AB') else x[0])

# List of type codes for narrowbody aircraft
# No regional aircraft like CRJ, ATR, or Dash 8 in this list
NB = ['A220', 'A318', 'A319', 'A320', 'A20N', 'A321', 'A21N', 'BCS1', 'BCS3',
      'B733','B734', 'B735','B737', 'B738', 'B739', 'B73J', 'B38M',
      'B39M', 'B752', 'B753', 'E75L', 'E75S','E190', 'E195', 'E290','E295']

# List of type codes for widebody aircraft
WB = ['A332', 'A333', 'A343', 'A346', 'A35K','A359', 'A388', 'B744','B763', 'B764',
      'B772', 'B773', 'B77L', 'B77W', 'B788', 'B789', 'B78X', 'B748']

# Filter only NB and WB flights
df_movements = df_movements[df_movements['typecode'].isin(NB + WB)]

# Modify the "isPushback" column and set it to TRUE if "parking_position" is one of "AB", "A", "B", "E", or "P"
df_movements['isPushback'] = df_movements.apply(
    lambda row: True if row['parking_position_gen'] in ['AB', 'A', 'B', 'E', 'P'] else False, axis=1)

# Labels
labels = ["##", "A", "B", "AB", "C", "D", "E", "F", "G", "H", "I", "P", "T", "V", "W"]
runways = ["##", "10", "16", "28", "32", "34"]

# Function to create a matrix of average values in meters from nautical miles
def create_avg_matrix(df_subset, row_labels, col_labels):
    # Initialize the matrix with zeros
    avg_matrix = np.zeros((len(row_labels), len(col_labels)), dtype='object')
    avg_matrix[0, :] = col_labels
    avg_matrix[:, 0] = row_labels

    # Calculate the mean values for each combination of runway and parking position
    for i in range(1, len(row_labels)):
        for j in range(1, len(col_labels)):
            runway = row_labels[i]
            parking_pos = col_labels[j]
            taxi_distances = df_subset[(df_subset['takeoffRunway'] == runway) & (df_subset['parking_position_gen'] == parking_pos)]['taxiDistance']
            
            if not taxi_distances.empty:
                avg_distance = taxi_distances.mean()
                avg_matrix[i, j] = str(int(avg_distance * 1852))  # Convert from nautical miles to meters
            else:
                avg_matrix[i, j] = "0"

    return avg_matrix

# Generate average distance matrices
avg_matrix_nb = create_avg_matrix(df_movements[df_movements['typecode'].isin(NB)], runways, labels)
avg_matrix_wb = create_avg_matrix(df_movements[df_movements['typecode'].isin(WB)], runways, labels)

# Convert to DataFrames (optional for display or export)
avg_matrix_nb_df = pd.DataFrame(avg_matrix_nb[1:, 1:], columns=labels[1:], index=runways[1:])
avg_matrix_wb_df = pd.DataFrame(avg_matrix_wb[1:, 1:], columns=labels[1:], index=runways[1:])

print("Narrowbody Avg Taxi Distance Matrix:\n", avg_matrix_nb_df)
print("Widebody Avg Taxi Distance Matrix:\n", avg_matrix_wb_df)

# Save the matrices as copyable tables
np.savetxt("Avg_Taxi_Distance_NB.txt", avg_matrix_nb, fmt="%s", delimiter="\t")
np.savetxt("Avg_Taxi_Distance_WB.txt", avg_matrix_wb, fmt="%s", delimiter="\t")

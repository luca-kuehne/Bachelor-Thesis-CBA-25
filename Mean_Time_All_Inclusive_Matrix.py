import pandas as pd
import numpy as np

# Read data
# Read df_movements (df_movements is the output of agps_proc.ipynb)
df_movements = pd.read_pickle('LSZH_MAY_SEP_df_movements.pkl')

# Filter for takeoffs
df_movements = df_movements[df_movements['isTakeoff'] == True]

# Remove takeoffs on Runway 14
df_movements = df_movements[df_movements['takeoffRunway'] != "14"]

# Extract the first letter of the parking position
df_movements['parking_position_gen'] = df_movements['parking_position'].astype(str).str[0]

# Lists of type codes
NB = ['A220', 'A318', 'A319', 'A320', 'A20N', 'A321', 'A21N', 'BCS1', 'BCS3',
      'B733', 'B734', 'B735', 'B737', 'B738', 'B739', 'B73J', 'B38M',
      'B39M', 'B752', 'B753', 'E75L', 'E75S', 'E190', 'E195', 'E290', 'E295']
WB = ['A332', 'A333', 'A343', 'A346', 'A35K', 'A359', 'A388', 'B744', 'B763', 'B764',
      'B772', 'B773', 'B77L', 'B77W', 'B788', 'B789', 'B78X', 'B748']

# Convert time columns to datetime
df_movements['lineupTime'] = pd.to_datetime(df_movements['lineupTime'])
df_movements['startTaxi'] = pd.to_datetime(df_movements['startTaxi'])
df_movements['startPushback'] = pd.to_datetime(df_movements['startPushback'])

# Calculate taxi duration depending on whether pushback was performed
df_movements['taxi_duration_calc'] = df_movements.apply(
    lambda row: row['lineupTime'] - row['startPushback']
    if row['isPushback'] and pd.notnull(row['startPushback'])
    else row['lineupTime'] - row['startTaxi']
    if pd.notnull(row['startTaxi'])
    else pd.NaT,
    axis=1
)

# Filter narrowbody and widebody flights with relevant columns
df_nb = df_movements[df_movements['typecode'].isin(NB)][['parking_position_gen', 'takeoffRunway', 'taxi_duration_calc']]
df_wb = df_movements[df_movements['typecode'].isin(WB)][['parking_position_gen', 'takeoffRunway', 'taxi_duration_calc']]

# Labels
labels = ["##", "A", "B", "C", "D", "E", "F", "G", "H", "I", "P", "T", "V", "W"]
runways = ["##", "10", "16", "28", "32", "34"]

# Function to create an average matrix with values in seconds
def create_avg_matrix_mmss_clean(df_subset, row_labels, col_labels):
    # Initialize matrix with zeros
    avg_matrix = np.zeros((len(row_labels), len(col_labels)), dtype='object')
    avg_matrix[0, :] = col_labels
    avg_matrix[:, 0] = row_labels

    # Calculate mean values for each combination of parking position and runway
    for i in range(1, len(row_labels)):
        for j in range(1, len(col_labels)):
            runway = row_labels[i]
            parking_pos = col_labels[j]
            taxi_durations = df_subset[(df_subset['takeoffRunway'] == runway) & (df_subset['parking_position_gen'] == parking_pos)]['taxi_duration_calc']
            
            if not taxi_durations.empty:
                avg_duration = taxi_durations.mean()
                avg_matrix[i, j] = str(int(avg_duration.total_seconds())) + "s"
            else:
                avg_matrix[i, j] = "0s"

    return avg_matrix

# Generate average duration matrices
avg_matrix_nb_mmss_clean = create_avg_matrix_mmss_clean(df_nb, runways, labels)
avg_matrix_wb_mmss_clean = create_avg_matrix_mmss_clean(df_wb, runways, labels)

# Convert to DataFrames (optional for display or export)
avg_matrix_nb_mmss_clean_df = pd.DataFrame(avg_matrix_nb_mmss_clean[1:, 1:], columns=labels[1:], index=runways[1:])
avg_matrix_wb_mmss_clean_df = pd.DataFrame(avg_matrix_wb_mmss_clean[1:, 1:], columns=labels[1:], index=runways[1:])

print("Narrowbody Avg Taxi Duration Matrix:\n", avg_matrix_nb_mmss_clean_df)
print("Widebody Avg Taxi Duration Matrix:\n", avg_matrix_wb_mmss_clean_df)

# Save the matrices as copyable tables
np.savetxt("Avg_Taxi_Duration_NB.txt", avg_matrix_nb_mmss_clean, fmt="%s", delimiter="\t")
np.savetxt("Avg_Taxi_Duration_WB.txt", avg_matrix_wb_mmss_clean, fmt="%s", delimiter="\t")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Information from literature review
year_1, cost_1 = 2030, 284.21
year_2, cost_2 = 2050, 909.48

# Create linear interpolation: y = m*x + b
m = (cost_2 - cost_1) / (year_2 - year_1)
b = cost_1 - m * year_1

# Define timespan
years = np.arange(2024, 2036)
costs = m * years + b

# Save as Dataframe
df = pd.DataFrame({'Year': years, 'Interpolated Cost ($/t CO2)': costs})

# Show results
print(df)

# Visualisation
plt.plot(years, costs, marker='o', label='Interpolated values')
plt.scatter([year_1, year_2], [cost_1, cost_2], color='red', label='Datapoints from literature')
plt.title('Linear Interpolation of social costs of CO2')
plt.xlabel('Year')
plt.ylabel('Costs in $/t CO₂')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

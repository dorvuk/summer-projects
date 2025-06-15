import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("./wdi-csv-zip-57-mb-/WDIData.csv")

# Define the higher ed indicator codes
higher_ed_codes = [
    'SE.TER.ENRR',         # Gross tertiary enrollment
    'SE.TER.CUAT.BA.ZS',   # Bachelor's+
    'SE.TER.CUAT.DO.ZS'    # Doctorate+
]

# Filter dataset for only those
filtered = df[df['Indicator Code'].isin(higher_ed_codes)]

# Melt years into rows
melted = filtered.melt(
    id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'],
    var_name='Year',
    value_name='Value'
)

melted = melted.dropna(subset=['Value'])
melted['Year'] = pd.to_numeric(melted['Year'], errors='coerce')
melted = melted.dropna(subset=['Year'])

# Pivot: country, year, indicator → value
pivot = melted.pivot_table(index=['Country Name', 'Year'], 
                           columns='Indicator Code', 
                           values='Value')

# Normalize each indicator per country (0–1), then average
pivot_norm = pivot.groupby(level=0).transform(lambda x: (x - x.min()) / (x.max() - x.min()))
pivot['CompositeIndex'] = pivot_norm.mean(axis=1)

# Reset index for regression
pivot = pivot.reset_index()

# Calculate slope of CompositeIndex for each country
slopes = []

for country, group in pivot.groupby('Country Name'):
    group = group.dropna(subset=['CompositeIndex'])
    if group['Year'].nunique() < 5:
        continue

    X = group['Year'].values.reshape(-1, 1)
    y = group['CompositeIndex'].values

    model = LinearRegression()
    model.fit(X, y)
    slope = model.coef_[0]

    if slope > 0:
        slopes.append((country, slope))

# Sort and plot
top = pd.DataFrame(slopes, columns=["Country", "Slope"]).sort_values(by='Slope', ascending=False).head(15)

# Plot
plt.figure(figsize=(10, 6))
plt.barh(top['Country'][::-1], top['Slope'][::-1])
plt.title("Top 15 Countries Increasing Higher Education Index the Fastest")
plt.xlabel("Normalized Slope (per year)")
plt.tight_layout()
plt.savefig("fastest_growing.png", dpi=300, bbox_inches='tight')
plt.show()

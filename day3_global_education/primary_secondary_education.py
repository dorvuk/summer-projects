import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load WDI data
data_path = "./wdi-csv-zip-57-mb-/WDIData.csv"
df = pd.read_csv(data_path)

# Filter only education indicators related to basic education
basic_edu_codes = [
    'SE.PRM.ENRR',   # Primary school enrollment (% gross)
    'SE.SEC.ENRR'    # Secondary school enrollment (% gross)
]

basic_df = df[df['Indicator Code'].isin(basic_edu_codes)]

# Reshape year columns into long format
melted = basic_df.melt(
    id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'],
    var_name='Year',
    value_name='Value'
)

# Clean data
melted = melted.dropna(subset=['Value'])
melted['Year'] = pd.to_numeric(melted['Year'], errors='coerce')
melted = melted.dropna(subset=['Year'])

# Global trend by year
global_trends = melted.groupby(['Year', 'Indicator Name'])['Value'].mean().reset_index()

# Plot
plt.figure(figsize=(12, 6))
sns.lineplot(data=global_trends, x='Year', y='Value', hue='Indicator Name', marker='o')

plt.title("Global Basic Education Enrollment Over Time")
plt.ylabel("Enrollment Rate (% gross)")
plt.xlabel("Year")
plt.legend(title='Indicator')
plt.grid(True)
plt.tight_layout()
plt.savefig("primary_secondary.png", dpi=300, bbox_inches='tight')
plt.show()

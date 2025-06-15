import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load WDI data
data_path = "./wdi-csv-zip-57-mb-/WDIData.csv"
df = pd.read_csv(data_path)

# Indicators for university/college-level education
tertiary_codes = [
    'SE.TER.ENRR',           # Gross enrollment in tertiary education
    'SE.TER.CUAT.BA.ZS',     # Population with bachelor's or higher
    'SE.TER.CUAT.DO.ZS',     # Population with doctorate
    'SE.TER.GRAD.FE.ZS',     # Female tertiary graduates (% of total)
    'SE.TER.GRAD.MA.ZS'      # Male tertiary graduates (% of total)
]

tertiary_df = df[df['Indicator Code'].isin(tertiary_codes)]

# Reshape year columns into rows
melted = tertiary_df.melt(
    id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'],
    var_name='Year',
    value_name='Value'
)

# Clean up
melted = melted.dropna(subset=['Value'])
melted['Year'] = pd.to_numeric(melted['Year'], errors='coerce')
melted = melted.dropna(subset=['Year'])

# Global trend over time
global_trends = melted.groupby(['Year', 'Indicator Name'])['Value'].mean().reset_index()
name_map = {
    "School enrollment, tertiary (% gross)": "Tertiary Enrollment",
    "Educational attainment, at least Bachelor's or equivalent, population 25+, total (%) (cumulative)": "Bachelor's+ Attainment",
    "Educational attainment, Doctoral or equivalent, population 25+, total (%) (cumulative)": "Doctorate+ Attainment"
}

global_trends["Indicator Name"] = global_trends["Indicator Name"].replace(name_map)


# Plot
plt.figure(figsize=(14, 7))
sns.lineplot(data=global_trends, x='Year', y='Value', hue='Indicator Name', marker='o')

plt.title("Global Trends in Higher Education")
plt.ylabel("Percentage or Gross Enrollment")
plt.xlabel("Year")
plt.grid(True)
plt.tight_layout()
plt.savefig("higher_education.png", dpi=300, bbox_inches='tight')
plt.show()


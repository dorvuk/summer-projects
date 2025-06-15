import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import pycountry
from sklearn.linear_model import LinearRegression
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Reuse the higher education indicators
higher_ed_codes = [
    'SE.TER.ENRR',         # Gross tertiary enrollment
    'SE.TER.CUAT.BA.ZS',   # Bachelor's+
    'SE.TER.CUAT.DO.ZS'    # Doctorate+
]

# Load data
df = pd.read_csv("./wdi-csv-zip-57-mb-/WDIData.csv")
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

# Pivot by country/year
pivot = melted.pivot_table(index=['Country Name', 'Year'],
                           columns='Indicator Code',
                           values='Value')

# Normalize per country and compute composite index
pivot_norm = pivot.groupby(level=0).transform(lambda x: (x - x.min()) / (x.max() - x.min()))
pivot['CompositeIndex'] = pivot_norm.mean(axis=1)
pivot = pivot.reset_index()

# Compute slope of CompositeIndex over time
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

# Load world basemap
world = gpd.read_file("./data/ne_110m_admin_0_countries.shp")

# Fix country naming issues
def clean_country(name):
    try:
        return pycountry.countries.lookup(name).name
    except:
        return name
    
manual_fixes = {
    "Brunei Darussalam": "Brunei",
    "Cabo Verde": "Cape Verde",
    "Congo, Dem. Rep.": "Democratic Republic of the Congo",
    "Congo, Rep.": "Republic of the Congo",
    "Cote d'Ivoire": "Ivory Coast",
    "Egypt, Arab Rep.": "Egypt",
    "Gambia, The": "Gambia",
    "Iran, Islamic Rep.": "Iran",
    "Korea, Rep.": "South Korea",
    "Lao PDR": "Laos",
    "Russian Federation": "Russia",
    "Venezuela, RB": "Venezuela",
    "Yemen, Rep.": "Yemen"
}

# Prepare slope data
education_growth_df = pd.DataFrame(slopes, columns=["Country", "Slope"])
education_growth_df['Country'] = education_growth_df['Country'].replace(manual_fixes)

# Merge slope data with world map
education_growth_df["Country"] = education_growth_df["Country"].apply(clean_country)
world["Country"] = world["SOVEREIGNT"].apply(clean_country)

merged = world.merge(education_growth_df, how="left", on="Country")

# Plot
fig, ax = plt.subplots(1, 1, figsize=(15, 9))
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="3%", pad=0.1)  # control width of colorbar

merged.plot(
    column='Slope',
    cmap='Blues',
    linewidth=0.5,
    ax=ax,
    edgecolor='0.8',
    legend=True,
    legend_kwds={
        'label': "Slope of Higher Education Index",
        'orientation': "vertical",
        'shrink': 0.5  # controls vertical size
    },
    vmax=0.05,  # limit upper color range to boost contrast
    vmin=0.010,  # optionally boost minimum so tiny values aren't ultra-white
    cax=cax,
    missing_kwds={"color": "lightgray", "label": "No data"}
)

ax.set_title('Global Growth in Higher Education (Composite Slope)', fontsize=16)
ax.axis('off')

plt.tight_layout()
plt.savefig("education_growth_world_map.png", dpi=300, bbox_inches='tight')
plt.show()

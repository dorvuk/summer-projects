import json
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import MultiPolygon
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Load scores
with open("combined_normalized_scores.json", "r", encoding="utf-8") as f:
    raw_scores = json.load(f)

# Load country name map
with open("country_name_map.json", "r", encoding="utf-8") as f:
    name_map = json.load(f)

def name_to_admin(name):
    return name_map.get(name, name)

# Load shapefile (Natural Earth 110m)
world = gpd.read_file("./data/ne_110m_admin_0_countries.shp")

# Prepare score mapping to shapefile
admin_score_map = {
    name_to_admin(name): None if val == "N/A" else float(val)
    for name, val in raw_scores.items()
}

# Assign scores
world["score"] = world["ADMIN"].map(admin_score_map)

# Plot map
fig, ax = plt.subplots(figsize=(18, 10))
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="3%", pad=0.1)

world.plot(
    ax=ax,
    column="score",
    cmap="Blues",
    edgecolor="0.8",
    linewidth=0.5,
    legend=True,
    legend_kwds={
        "label": "Gaming Skill Score (0–100)",
        "orientation": "vertical",
        "shrink": 0.5
    },
    missing_kwds={
        "color": "lightgray",
        "label": "No Data"
    },
    cax=cax
)

ax.set_title("Average Gaming Skill by Country", fontsize=18)
ax.axis("off")
plt.tight_layout()
plt.savefig("world_gaming_skill_map.png", dpi=300, bbox_inches="tight")
plt.show()

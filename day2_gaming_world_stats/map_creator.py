import json
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import MultiPolygon

# === Load data ===

# Load scores
with open("combined_normalized_scores.json", "r", encoding="utf-8") as f:
    raw_scores = json.load(f)

# Load country name fixes
with open("country_name_map.json", "r", encoding="utf-8") as f:
    name_map = json.load(f)

def name_to_admin(name):
    return name_map.get(name, name)

# === Load and prepare shapefile ===

# Load shapefile
world = gpd.read_file("./data/ne_110m_admin_0_countries.shp")

# Simplify geometries for faster drawing
world["geometry"] = world["geometry"].apply(
    lambda g: max(g.geoms, key=lambda x: x.area) if isinstance(g, MultiPolygon) else g
)

# === Match scores to country ADMIN names ===

admin_score_map = {
    name_to_admin(name): None if val == "N/A" else float(val)
    for name, val in raw_scores.items()
}

# Assign scores
world["score"] = world["ADMIN"].map(admin_score_map)


# === Plot map ===

fig, ax = plt.subplots(figsize=(18, 10))
world.boundary.plot(ax=ax, linewidth=0.5, color="black")

world.plot(
    ax=ax,
    column="score",
    cmap="Blues",
    edgecolor="0.8",
    linewidth=0.5,
    legend=True,
    legend_kwds={
        "shrink": 0.6,
        "label": "Gaming Skill Score"
    },
    missing_kwds={
        "color": "lightgray",
        "label": "No Data"
    }
)

ax.set_title("Average Gaming Skill", fontsize=18)
ax.axis("off")
plt.tight_layout()
plt.savefig("world_gaming_skill_map.png", dpi=300)
plt.show()

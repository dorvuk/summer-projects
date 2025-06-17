import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ─── CONFIGURABLE SETTINGS ─────────────────────────────────────────────────────

# Operators and their display characters
operators = {
    "plus": "+",
    "minus": "—",
    "divide": "/",
    "times": "•"
}

# Paths to fonts installed on your system
font_paths = [
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/georgia.ttf",
    "C:/Windows/Fonts/times.ttf",
    "C:/Windows/Fonts/calibri.ttf"
]

output_dir     = "operator_dataset"    # where subfolders plus/, minus/, etc. live
samples_per_op = 300                  # 300 samples each
canvas_size    = (64, 64)             # large canvas to prevent clipping
final_size     = (28, 28)             # MNIST‐style output size

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def load_random_font():
    """Pick a random font and size."""
    path = random.choice(font_paths)
    size = random.randint(28, 40)
    try:
        return ImageFont.truetype(path, size)
    except IOError:
        return ImageFont.load_default()

def generate_operator_image(symbol, index, out_folder):
    """Generate one sample of `symbol` and save it as <label>_<index>.png."""
    # 1) blank large canvas
    img = Image.new("L", canvas_size, 0)
    draw = ImageDraw.Draw(img)

    # 2) pick random font
    font = load_random_font()

    # 3) measure symbol and compute centered position with random displacement
    bbox = font.getbbox(symbol)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    # base center
    cx = (canvas_size[0] - w) // 2 - bbox[0]
    cy = (canvas_size[1] - h) // 2 - bbox[1]
    # random slight displacement (±5 px)
    dx = random.randint(-5, 5)
    dy = random.randint(-5, 5)
    pos = (cx + dx, cy + dy)

    # 4) draw the symbol
    draw.text(pos, symbol, font=font, fill=255)

    # 5) apply a random slight rotation (±20°), no expand
    angle = random.uniform(-20, 20)
    img = img.rotate(angle, fillcolor=0)

    # 6) optional blur for variation
    if random.random() < 0.4:
        img = img.filter(ImageFilter.GaussianBlur(random.uniform(0.5, 1.2)))

    # 7) downsize to 28×28
    img = img.resize(final_size, Image.LANCZOS)

    # 8) save with correct naming
    label = os.path.basename(out_folder)
    filename = f"{label}_{index}.png"
    img.save(os.path.join(out_folder, filename))

# ─── MAIN GENERATION LOOP ──────────────────────────────────────────────────────

for label, symbol in operators.items():
    folder = os.path.join(output_dir, label)
    os.makedirs(folder, exist_ok=True)
    print(f"Generating {samples_per_op} samples for '{label}'…")
    for i in range(samples_per_op):
        generate_operator_image(symbol, i + 1, folder)

print("Done: operator_dataset populated with 300 samples per class.")

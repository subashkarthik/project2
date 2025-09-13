
import csv
import math

def load_color_dataset(path):
    """
    Reads dataset/colors.csv with columns:
      name,r,g,b,hex
    Returns list of dicts with keys: name,r,g,b,hex
    """
    colors = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                colors.append({
                    "name": r["name"].strip(),
                    "r": int(r["r"]),
                    "g": int(r["g"]),
                    "b": int(r["b"]),
                    "hex": r.get("hex", "").strip() or rgb_to_hex((int(r["r"]), int(r["g"]), int(r["b"]))),
                })
            except Exception:
                # skip malformed rows
                continue
    return colors

def rgb_to_hex(rgb):
    """(r,g,b) -> '#rrggbb'"""
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2])).upper()

def pretty_rgb(rgb):
    return f"({int(rgb[0])}, {int(rgb[1])}, {int(rgb[2])})"

def euclidean_rgb(a, b):
    """Euclidean distance in RGB space"""
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

def find_nearest_color(target_rgb, color_db):
    """Return nearest color dict with added 'distance' key"""
    if not color_db:
        return None
    best = None
    best_d = float("inf")
    for c in color_db:
        d = euclidean_rgb(target_rgb, (c["r"], c["g"], c["b"]))
        if d < best_d:
            best_d = d
            best = c.copy()
    if best is not None:
        best["distance"] = best_d
    return best

# utils.py
import os
import math
import numpy as np
import pandas as pd

def _find_col(df, names):
    """Return the actual column name from df that matches any candidate in names (case-insensitive)."""
    cols = {c.lower(): c for c in df.columns}
    for n in names:
        if n.lower() in cols:
            return cols[n.lower()]
    return None

def load_color_dataset(path):
    """
    Load a colours CSV from path and return a list-of-dicts representing colours.
    Accepts CSVs with a variety of column names. Expected columns (case-insensitive):
      - name (or colorname)
      - r / red
      - g / green
      - b / blue
      - hex
    If `name` is missing, the loader will create a human-readable name from the hex code.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Color dataset not found at: {path}")

    df = pd.read_csv(path, dtype=str)  # read as str to avoid surprises, convert later
    # find columns
    name_col = _find_col(df, ["name", "colorname", "colour", "colourname", "color_name"])
    r_col = _find_col(df, ["r", "red"])
    g_col = _find_col(df, ["g", "green"])
    b_col = _find_col(df, ["b", "blue"])
    hex_col = _find_col(df, ["hex", "hexcode", "hex_value", "hexvalue"])

    # if no hex but RGB present, create hex
    if hex_col is None and r_col and g_col and b_col:
        df["hex"] = df.apply(lambda row: "#{:02X}{:02X}{:02X}".format(int(float(row[r_col])), int(float(row[g_col])), int(float(row[b_col]))), axis=1)
        hex_col = "hex"

    # if no name, create from hex
    if name_col is None and hex_col is not None:
        df["name"] = df[hex_col].apply(lambda h: f"Color {str(h).upper()}")
        name_col = "name"

    # require at least r,g,b or hex
    if not (r_col and g_col and b_col) and hex_col is None:
        raise ValueError("Dataset must contain either R,G,B columns or a HEX column.")

    # Build list of dicts with normalized types
    colors = []
    for _, row in df.iterrows():
        # get or parse RGB
        if r_col and g_col and b_col:
            try:
                r = int(float(row[r_col]))
                g = int(float(row[g_col]))
                b = int(float(row[b_col]))
            except Exception:
                # fallback to parsing hex
                hx = str(row[hex_col]).lstrip("#")
                r = int(hx[0:2], 16); g = int(hx[2:4], 16); b = int(hx[4:6], 16)
        else:
            hx = str(row[hex_col]).lstrip("#")
            r = int(hx[0:2], 16); g = int(hx[2:4], 16); b = int(hx[4:6], 16)

        name = str(row[name_col]) if name_col else f"Color #{r:02X}{g:02X}{b:02X}"
        hexv = str(row[hex_col]).upper() if hex_col else "#{:02X}{:02X}{:02X}".format(r, g, b)
        colors.append({"name": name, "r": int(r), "g": int(g), "b": int(b), "hex": hexv})

    return colors


def rgb_to_hex(rgb):
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


def pretty_rgb(rgb):
    return f"({int(rgb[0])}, {int(rgb[1])}, {int(rgb[2])})"


def find_nearest_color(target_rgb, color_db):
    """
    target_rgb: (r,g,b) tuple
    color_db: list of dicts as returned by load_color_dataset
    Returns: dict with keys: name, r, g, b, hex, distance
    """
    if color_db is None or len(color_db) == 0:
        return None

    # Convert color_db to numpy array for fast distance computation
    arr = np.array([[c["r"], c["g"], c["b"]] for c in color_db], dtype=np.int32)
    target = np.array(target_rgb, dtype=np.int32)
    dif = arr - target
    d2 = np.sum(dif * dif, axis=1)  # squared dist
    idx = int(np.argmin(d2))
    best = color_db[idx].copy()
    best["distance"] = float(math.sqrt(float(d2[idx])))
    return best

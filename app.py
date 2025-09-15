import streamlit as st
from PIL import Image
import numpy as np
import os
from utils import load_color_dataset, rgb_to_hex, find_nearest_color, pretty_rgb
from streamlit_image_coordinates import streamlit_image_coordinates

st.set_page_config(page_title="Colour Detection (Click a pixel)", page_icon="🎨", layout="centered")

st.title("🎨 Colour Detection — Click a pixel to get exact colour")

st.markdown(
    """
Upload an image, then click anywhere on the image to get **exact RGB**, **HEX** and the **nearest named colour** from the dataset.
"""
)

# Prepare dataset
DATA_PATH = os.path.join("colours1.csv")
color_db = load_color_dataset(DATA_PATH)

uploaded_file = st.file_uploader("Upload an image (PNG / JPG / JPEG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Open image with PIL
    image = Image.open(uploaded_file).convert("RGB")
    st.write("Uploaded image:")
    # Display the image and capture click coordinates using the component
    max_width = st.session_state.get("max_width", 700)
    coords = streamlit_image_coordinates(
    image,
    key="pil",
    height=None,   # optional
)

    st.image(image, use_column_width=True)

    if coords and coords != {}:
        # coords is dict: {'x': int, 'y': int, 'width': int, 'height': int}
        x = coords.get("x")
        y = coords.get("y")
        st.write(f"Clicked at image pixel coordinates: **x={x}**, **y={y}**")

        # Convert PIL image to numpy array and get pixel
        arr = np.array(image)
        h, w = arr.shape[:2]

        # coords from component are already relative to image pixel coordinates, but clamp just in case
        x = int(max(0, min(w - 1, x)))
        y = int(max(0, min(h - 1, y)))

        r, g, b = tuple(arr[y, x])
        hex_code = rgb_to_hex((r, g, b))
        st.write("**Exact colour at clicked pixel:**")
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"<div style='width:120px;height:80px;border-radius:6px;background:{hex_code};'></div>", unsafe_allow_html=True)
        with col2:
            st.write(f"- RGB: {pretty_rgb((r,g,b))}")
            st.write(f"- HEX: `{hex_code}`")

        # Find nearest named color
        nearest = find_nearest_color((r, g, b), color_db)
        if nearest:
            name = nearest["name"]
            nrgb = (nearest["r"], nearest["g"], nearest["b"])
            ndist = nearest["distance"]
            nhex = rgb_to_hex(nrgb)
            st.markdown("**Nearest named colour (from dataset):**")
            c1, c2 = st.columns([1, 3])
            with c1:
                st.markdown(f"<div style='width:90px;height:60px;border-radius:6px;background:{nhex};'></div>", unsafe_allow_html=True)
            with c2:
                st.write(f"**{name}**")
                st.write(f"- RGB: {pretty_rgb(nrgb)}")
                st.write(f"- HEX: `{nhex}`")
                st.write(f"- Distance (RGB Euclidean): {ndist:.2f}")

    else:
        st.info("Click anywhere on the image above to inspect the colour of that pixel.")
else:
    st.info("Upload an image to begin.")


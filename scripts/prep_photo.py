"""Prep a photo for ASCII conversion: remove background, boost contrast, composite on white."""
import sys
import os
import io

import numpy as np
from PIL import Image
from rembg import remove
import cv2


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <photo_path>")
        sys.exit(1)

    photo_path = sys.argv[1]
    if not os.path.exists(photo_path):
        print(f"File not found: {photo_path}")
        sys.exit(1)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    out_path = os.path.join(data_dir, "source-prepped.png")

    # 1. Remove background (using exact Attempt 1 logic)
    with open(photo_path, "rb") as f:
        raw = f.read()
    nobg_bytes = remove(raw)
    img_nobg = Image.open(io.BytesIO(nobg_bytes)).convert("RGBA")

    # 2. Composite onto white
    white = Image.new("RGBA", img_nobg.size, (255, 255, 255, 255))
    composite = Image.alpha_composite(white, img_nobg).convert("L")  # grayscale
    
    # Crop the image tightly to the person so there is no extra padding!
    arr_temp = np.array(composite)
    non_white = arr_temp < 250
    if np.any(non_white):
        coords = np.argwhere(non_white)
        y0, x0 = coords.min(axis=0)
        y1, x1 = coords.max(axis=0)
        # Add a tiny 5px pad
        y0 = max(0, y0 - 5)
        y1 = min(arr_temp.shape[0], y1 + 5)
        x0 = max(0, x0 - 5)
        x1 = min(arr_temp.shape[1], x1 + 5)
        composite = composite.crop((x0, y0, x1, y1))

    # 3. Boost local contrast with CLAHE
    arr = np.array(composite)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(arr)

    Image.fromarray(enhanced).save(out_path)
    print(f"✓ Prepped photo → {out_path}")


if __name__ == "__main__":
    main()

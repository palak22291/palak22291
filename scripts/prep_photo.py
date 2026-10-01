"""Prep a photo for ASCII conversion: remove background, boost contrast, composite on white."""
import sys
import os

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

    # 1. Remove background
    with open(photo_path, "rb") as f:
        raw = f.read()
    nobg = remove(raw)
    img = Image.open(__import__("io").BytesIO(nobg)).convert("RGBA")

    # 2. Composite onto white
    white = Image.new("RGBA", img.size, (255, 255, 255, 255))
    composite = Image.alpha_composite(white, img).convert("L")  # grayscale

    # 3. Boost local contrast with CLAHE
    arr = np.array(composite)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(arr)

    Image.fromarray(enhanced).save(out_path)
    print(f"✓ Prepped photo → {out_path}")


if __name__ == "__main__":
    main()

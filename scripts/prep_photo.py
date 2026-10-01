"""Prep a photo for ASCII conversion: remove background, boost contrast, composite on white."""
import sys
import os
import io

import numpy as np
from PIL import Image, ImageOps
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

    # 0. Fix EXIF orientation (prevents the image from being tilted/rotated)
    img_orig = Image.open(photo_path)
    img_orig = ImageOps.exif_transpose(img_orig)
    
    # Save the upright image to a byte buffer for rembg
    buf = io.BytesIO()
    img_orig.save(buf, format="PNG")
    raw_bytes = buf.getvalue()

    # 1. Remove background
    nobg_bytes = remove(raw_bytes)
    img_nobg = Image.open(io.BytesIO(nobg_bytes)).convert("RGBA")

    # 2. Composite onto white
    white = Image.new("RGBA", img_nobg.size, (255, 255, 255, 255))
    composite = Image.alpha_composite(white, img_nobg).convert("L")  # grayscale

    # 3. Boost local contrast with CLAHE
    arr = np.array(composite)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(arr)

    Image.fromarray(enhanced).save(out_path)
    print(f"✓ Prepped photo → {out_path}")


if __name__ == "__main__":
    main()

"""Prep a photo for ASCII conversion: remove background, crop to square, boost contrast."""
import sys
import os
import numpy as np
from PIL import Image
from rembg import remove
import cv2

def crop_to_square(img_arr):
    # img_arr is grayscale, white background (255)
    # Find bounding box of non-white pixels
    non_white = img_arr < 250
    coords = np.argwhere(non_white)
    
    if coords.size == 0:
        return img_arr # Empty image
        
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)
    
    # Add a little padding
    pad = 20
    h_img, w_img = img_arr.shape
    y0 = max(0, y0 - pad)
    y1 = min(h_img, y1 + pad)
    x0 = max(0, x0 - pad)
    x1 = min(w_img, x1 + pad)
    
    cropped = img_arr[y0:y1, x0:x1]
    
    # Now make it a square by cropping height to width (from top), or width to height
    h, w = cropped.shape
    size = min(h, w)
    
    if h > w:
        # crop bottom to make square (keep top/face)
        return cropped[:w, :]
    elif w > h:
        # crop sides to make square (keep center)
        diff = (w - h) // 2
        return cropped[:, diff:diff+h]
    else:
        return cropped

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
    
    # 3. Crop to square focusing on the subject
    arr = np.array(composite)
    square_arr = crop_to_square(arr)

    # 4. Boost local contrast with CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(square_arr)

    Image.fromarray(enhanced).save(out_path)
    print(f"✓ Prepped photo → {out_path}")


if __name__ == "__main__":
    main()

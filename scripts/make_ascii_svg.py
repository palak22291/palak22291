"""Convert prepped grayscale photo into a self-typing monochrome ASCII SVG."""
import os
from PIL import Image

# Brightness ramp: sparse (bright) → dense (dark)
RAMP = " .`:-=+*cs#%@"

COLS = 100
CHAR_ASPECT = 0.55  # monospace characters are taller than wide

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = os.path.join(project_root, "data", "source-prepped.png")

    if not os.path.exists(src):
        print(f"Source not found: {src}\nRun prep_photo.py first.")
        return

    img = Image.open(src).convert("L")
    w, h = img.size

    # Resize to target columns, accounting for character aspect ratio
    rows = int(COLS * (h / w) * CHAR_ASPECT)
    img = img.resize((COLS, rows))
    pixels = img.load()

    # Build ASCII rows
    ascii_rows: list[str] = []
    for y in range(rows):
        row = []
        for x in range(COLS):
            brightness = pixels[x, y]
            # INVERT MAPPING: White (255) becomes RAMP[0] (' '), Black (0) becomes RAMP[-1] ('@')
            idx = int((255 - brightness) / 255 * (len(RAMP) - 1))
            row.append(RAMP[idx])
        ascii_rows.append("".join(row))

    # SVG parameters
    font_size = 7
    line_height = 8.5
    svg_w = 370
    svg_h = int(rows * line_height) + 20

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" '
        f'viewBox="0 0 {svg_w} {svg_h}">',
        "  <style>",
        "    @keyframes typeRow {",
        "      from { clip-path: inset(0 100% 0 0); }",
        "      to   { clip-path: inset(0 0% 0 0); }",
        "    }",
        "    .row {",
        "      clip-path: inset(0 100% 0 0);",
        "      animation: typeRow .4s ease-out forwards;",
        "    }",
        "  </style>",
    ]

    for i, row_text in enumerate(ascii_rows):
        delay = i * 0.03
        y = 10 + i * line_height
        # Escape XML special chars
        safe = row_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        lines.append(
            f'  <text x="5" y="{y:.1f}" '
            f'font-family="\'Consolas\',\'Monaco\',monospace" '
            f'font-size="{font_size}" fill="#8b949e" '
            f'class="row" style="animation-delay:{delay:.2f}s">'
            f"{safe}</text>"
        )

    lines.append("</svg>")

    out = os.path.join(project_root, "palak-ascii.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"✓ ASCII portrait ({COLS}×{rows}) → {out}")

if __name__ == "__main__":
    main()

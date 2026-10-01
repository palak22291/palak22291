"""Render contribution data as an animated SVG heatmap (53-week calendar)."""
import os
import json
import datetime


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_file = os.path.join(project_root, "data", "contributions.json")

    if not os.path.exists(data_file):
        print(f"Data file {data_file} not found. Run fetch_contributions.py first.")
        return

    with open(data_file, "r") as f:
        data = json.load(f)

    contributions = data.get("contributions", [])
    stats = data.get("stats", {})
    total = stats.get("total_contributions", 0)

    # --- Build a date→level lookup ---
    level_map: dict[str, int] = {}
    for day in contributions:
        level_map[day["date"]] = day.get("level", 0)

    # --- Build the 53-week × 7-day grid from the date range ---
    if not contributions:
        print("No contribution data.")
        return

    dates = sorted(level_map.keys())
    start = datetime.date.fromisoformat(dates[0])
    end = datetime.date.fromisoformat(dates[-1])

    # Align start to Sunday (weekday 6 in Python = Sunday)
    while start.weekday() != 6:
        start -= datetime.timedelta(days=1)

    weeks: list[list[tuple[str, int]]] = []
    current = start
    week: list[tuple[str, int]] = []
    while current <= end:
        ds = current.isoformat()
        week.append((ds, level_map.get(ds, 0)))
        if len(week) == 7:
            weeks.append(week)
            week = []
        current += datetime.timedelta(days=1)
    if week:
        weeks.append(week)

    # --- SVG constants ---
    box = 11
    gap = 3
    step = box + gap
    rx, ry = 2, 2
    colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
    pad_x = 45
    pad_y = 55
    width = 860

    grid_h = 7 * step
    footer_y = pad_y + grid_h + 25
    height = footer_y + 20

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        "  <style>",
        "    @keyframes slideIn {",
        "      from { opacity: 0; transform: translateY(8px); }",
        "      to   { opacity: 1; transform: translateY(0); }",
        "    }",
        "    .col { opacity: 0; animation: slideIn .45s ease forwards; }",
        '    .title { font-family: "Consolas","Monaco",monospace; fill: #58a6ff; font-size: 14px; }',
        '    .label { font-family: -apple-system,sans-serif; fill: #8b949e; font-size: 10px; }',
        '    .foot  { font-family: -apple-system,sans-serif; fill: #8b949e; font-size: 12px; }',
        "  </style>",
        "",
        f'  <text x="{pad_x}" y="25" class="title">palak@github ~ $ ./contributions.sh</text>',
    ]

    # --- month labels (first occurrence of each month at correct x position) ---
    seen_months: set[str] = set()
    for ci, wk in enumerate(weeks):
        if not wk:
            continue
        d = wk[0][0]
        dt = datetime.date.fromisoformat(d)
        key = f"{dt.year}-{dt.month:02d}"
        if key not in seen_months:
            seen_months.add(key)
            mon = dt.strftime("%b")
            x = pad_x + ci * step
            lines.append(f'  <text x="{x}" y="{pad_y - 10}" class="label">{mon}</text>')

    # --- day labels ---
    for row, lbl in {1: "Mon", 3: "Wed", 5: "Fri"}.items():
        y = pad_y + row * step + 9
        lines.append(f'  <text x="{pad_x - 30}" y="{y}" class="label">{lbl}</text>')

    # --- draw boxes ---
    for ci, wk in enumerate(weeks):
        delay = ci * 0.018
        lines.append(f'  <g class="col" style="animation-delay:{delay:.3f}s">')
        x = pad_x + ci * step
        for ri, (_, lvl) in enumerate(wk):
            y = pad_y + ri * step
            color = colors[min(lvl, len(colors) - 1)]
            lines.append(
                f'    <rect x="{x}" y="{y}" width="{box}" height="{box}" '
                f'rx="{rx}" ry="{ry}" fill="{color}"/>'
            )
        lines.append("  </g>")

    # --- footer ---
    lines.append(
        f'  <text x="{pad_x}" y="{footer_y}" class="foot">'
        f"{total} contributions in the last year</text>"
    )

    # --- Less → More legend ---
    legend_x = width - 150
    lines.append(f'  <text x="{legend_x - 28}" y="{footer_y}" class="label">Less</text>')
    for i, c in enumerate(colors):
        lx = legend_x + i * step
        lines.append(
            f'  <rect x="{lx}" y="{footer_y - 10}" width="{box}" height="{box}" '
            f'rx="{rx}" ry="{ry}" fill="{c}"/>'
        )
    lines.append(
        f'  <text x="{legend_x + len(colors) * step + 4}" y="{footer_y}" class="label">More</text>'
    )

    lines.append("</svg>")

    out = os.path.join(project_root, "contrib-heatmap.svg")
    with open(out, "w") as f:
        f.write("\n".join(lines))
    print(f"✓ Rendered heatmap ({len(weeks)} weeks) → {out}")


if __name__ == "__main__":
    main()

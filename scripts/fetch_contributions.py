"""Fetch real GitHub contribution data for palak22291 (no API token needed)."""
import os
import json
import re
import requests
from bs4 import BeautifulSoup


def main():
    username = "palak22291"
    url = f"https://github.com/users/{username}/contributions"

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching contributions: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract exact total from h2
    total_count = 0
    h2 = soup.find("h2", class_="f4 text-normal mb-2")
    if h2:
        m = re.search(r'([\d,]+)', h2.text)
        if m:
            total_count = int(m.group(1).replace(',', ''))

    days = soup.find_all("td", class_="ContributionCalendar-day")

    contributions = []
    current_streak = 0
    longest_streak = 0
    best_count = 0
    best_date = None

    for day in days:
        date = day.get("data-date")
        level_str = day.get("data-level")
        day_id = day.get("id")
        
        if not date or level_str is None:
            continue
            
        try:
            level = int(level_str)
        except ValueError:
            level = 0
            
        # Parse exact count from tooltip
        count = 0
        if day_id:
            tooltip = soup.find("tool-tip", attrs={"for": day_id})
            if tooltip:
                text = tooltip.text.strip()
                if "No" not in text:
                    m = re.search(r'^([\d,]+)', text)
                    if m:
                        count = int(m.group(1).replace(',', ''))

        contributions.append({"date": date, "level": level, "count": count})

        if count > 0:
            current_streak += 1
            longest_streak = max(longest_streak, current_streak)
            if count > best_count:
                best_count = count
                best_date = date
        else:
            current_streak = 0

    # Ensure total is accurate
    calculated_total = sum(d["count"] for d in contributions)
    if total_count == 0:
        total_count = calculated_total

    data = {
        "contributions": contributions,
        "stats": {
            "total_contributions": total_count,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "best_day": best_date,
            "best_day_level": best_count,
        },
    }

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    output_file = os.path.join(data_dir, "contributions.json")
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✓ Saved {len(contributions)} days ({total_count} contributions) → {output_file}")


if __name__ == "__main__":
    main()

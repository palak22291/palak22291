"""Fetch real GitHub contribution data for palak22291 (no API token needed)."""
import os
import json
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
    days = soup.find_all("td", class_="ContributionCalendar-day")

    contributions = []
    total = 0
    current_streak = 0
    longest_streak = 0
    best_count = 0
    best_date = None

    for day in days:
        date = day.get("data-date")
        level_str = day.get("data-level")
        if not date or level_str is None:
            continue
        try:
            level = int(level_str)
        except ValueError:
            continue

        contributions.append({"date": date, "level": level})

        if level > 0:
            current_streak += 1
            longest_streak = max(longest_streak, current_streak)
            total += level
            if level > best_count:
                best_count = level
                best_date = date
        else:
            current_streak = 0

    data = {
        "contributions": contributions,
        "stats": {
            "total_contributions": total,
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

    print(f"✓ Saved {len(contributions)} days ({total} contributions) → {output_file}")


if __name__ == "__main__":
    main()

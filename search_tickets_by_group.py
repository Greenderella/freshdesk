import time
from datetime import date, timedelta

import requests
from decouple import config


DOMAIN = config("FRESHDESK_DOMAIN", default="https://bitwarden.freshdesk.com").rstrip("/")
API_KEY = config("API_KEY")
AUTH = (API_KEY, "X")

GROUP_IDS = [
    19000157557,
    19000156967,
]

PRIORITIES = [1, 2, 3, 4]

# END_DATE is exclusive.
START_DATE = date(2026, 6, 29)
END_DATE = date(2026, 7, 7)

# Use created_at to match your Freshdesk export filter: "Created time / Last 7 days".
# Change this to "updated_at" only if you intentionally want tickets updated during the period.
SEARCH_DATE_FIELD = "created_at"


def freshdesk_get(path, params=None):
    while True:
        response = requests.get(
            f"{DOMAIN}{path}",
            auth=AUTH,
            params=params,
            timeout=60,
        )

        if response.status_code == 429:
            wait = int(response.headers.get("Retry-After", "60"))
            print(f"Rate limited. Waiting {wait} seconds...")
            time.sleep(wait + 2)
            continue

        if response.status_code != 200:
            print("Freshdesk request failed")
            print("URL:", response.url)
            print("Status:", response.status_code)
            print("Body:", response.text[:500])
            response.raise_for_status()

        return response.json()


def daterange(start_date, end_date):
    current = start_date

    while current < end_date:
        yield current
        current += timedelta(days=1)


def run_search(query):
    found_ids = set()

    for page in range(1, 11):
        data = freshdesk_get(
            "/api/v2/search/tickets",
            params={
                "query": f'"{query}"',
                "page": page,
            },
        )

        total = data.get("total", 0)
        results = data.get("results", [])

        if page == 1:
            print(f"Total found: {total}")

        for ticket in results:
            found_ids.add(ticket["id"])

        if not results or page * 30 >= total:
            break

        time.sleep(0.3)

    return found_ids, total


ticket_ids = set()

for current_date in daterange(START_DATE, END_DATE):
    for group_id in GROUP_IDS:
        base_query = (
            f"group_id:{group_id} "
            f"AND {SEARCH_DATE_FIELD}:'{current_date.isoformat()}'"
        )

        print(f"\nSearching: {base_query}")
        ids, total = run_search(base_query)

        if total <= 300:
            ticket_ids.update(ids)
            continue

        print("More than 300 found. Splitting by priority...")

        for priority in PRIORITIES:
            priority_query = f"{base_query} AND priority:{priority}"
            print(f"Searching: {priority_query}")

            priority_ids, priority_total = run_search(priority_query)

            if priority_total > 300:
                print(
                    "WARNING: Still more than 300 tickets found even after splitting by priority. "
                    "This needs another split."
                )

            ticket_ids.update(priority_ids)

print("\nDone.")
print(f"Unique ticket IDs found: {len(ticket_ids)}")

with open("ticket_ids_from_search.txt", "w", encoding="utf-8") as f:
    for ticket_id in sorted(ticket_ids):
        f.write(f"{ticket_id}\n")

print("Saved ticket IDs to ticket_ids_from_search.txt")
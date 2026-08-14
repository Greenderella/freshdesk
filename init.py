import time

import requests
from decouple import config

import databases


DOMAIN = config("FRESHDESK_DOMAIN", default="https://bitwarden.freshdesk.com").rstrip("/")
API_KEY = config("API_KEY")
AUTH = (API_KEY, "X")

TICKET_IDS_FILE = "ticket_ids_from_search.txt"
SKIPPED_TICKETS_FILE = "skipped_ticket_ids.txt"


def freshdesk_get(path, params=None, allow_404=False):
    while True:
        response = requests.get(
            f"{DOMAIN}{path}",
            auth=AUTH,
            params=params,
            timeout=60,
        )

        print(".", end="", flush=True)

        if response.status_code == 429:
            wait = int(response.headers.get("Retry-After", "60"))
            print(f"\nRate limited. Waiting {wait} seconds...")
            time.sleep(wait + 2)
            continue

        if response.status_code == 404 and allow_404:
            return None

        if response.status_code != 200:
            print("\nFreshdesk request failed")
            print("URL:", response.url)
            print("Status:", response.status_code)
            print("Body preview:", response.text[:500])
            response.raise_for_status()

        return response.json()


def read_ticket_ids():
    with open(TICKET_IDS_FILE, "r", encoding="utf-8") as file:
        return [
            int(line.strip())
            for line in file
            if line.strip()
        ]


def ticket_already_saved(cur, ticket_id):
    cur.execute("SELECT 1 FROM tickets WHERE id = ?", (ticket_id,))
    return cur.fetchone() is not None


def log_skipped_ticket(ticket_id, reason):
    with open(SKIPPED_TICKETS_FILE, "a", encoding="utf-8") as file:
        file.write(f"{ticket_id},{reason}\n")


def get_ticket(ticket_id):
    return freshdesk_get(
        f"/api/v2/tickets/{ticket_id}",
        allow_404=True,
    )


def get_conversations(ticket_id):
    all_conversations = []
    page = 1

    while True:
        conversations = freshdesk_get(
            f"/api/v2/tickets/{ticket_id}/conversations",
            params={"page": page},
            allow_404=True,
        )

        if conversations is None:
            log_skipped_ticket(ticket_id, "conversations_404")
            break

        if not conversations:
            break

        all_conversations.extend(conversations)
        page += 1
        time.sleep(0.2)

    return all_conversations


conn = databases.connect_and_create()
cur = conn.cursor()

ticket_ids = read_ticket_ids()

print(f"Fetching {len(ticket_ids)} tickets from {TICKET_IDS_FILE}")

for index, ticket_id in enumerate(ticket_ids, start=1):
    if ticket_already_saved(cur, ticket_id):
        print(f"\nSkipping ticket {ticket_id} ({index}/{len(ticket_ids)}) - already saved")
        continue

    print(f"\nFetching ticket {ticket_id} ({index}/{len(ticket_ids)})")

    ticket = get_ticket(ticket_id)

    if ticket is None:
        print(f"\nSkipping ticket {ticket_id} - Freshdesk returned 404")
        log_skipped_ticket(ticket_id, "ticket_404")
        continue

    databases.save_ticket(cur, ticket)

    for conversation in get_conversations(ticket_id):
        databases.save_conversation(cur, conversation)

    for tag in ticket.get("tags", []):
        databases.save_tag(cur, ticket["id"], tag)

    conn.commit()
    time.sleep(0.3)

conn.commit()
conn.close()

print("\nDone.")
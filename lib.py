import re
import time
import requests as r
from decouple import config


def get_next_link(link_header):
    if not link_header:
        return None

    links = link_header.split(",")

    for link in links:
        if 'rel="next"' in link:
            match = re.search(r"<(.*?)>", link)
            if match:
                return match.group(1)

    # Fallback for older/simple Freshdesk link headers
    match = re.search(r"<(.*?)>", link_header)
    if match:
        return match.group(1)

    return None


class FreshdeskIterator:
    def __init__(self, url):
        self.url = url

    def __iter__(self):
        self.memory = []
        self.count = 1
        self.query = None
        return self

    def __next__(self):
        if not self.memory:
            if self.count == 1:
                desk = config("FRESHDESK_DOMAIN", default="https://bitwarden.freshdesk.com")
                next_url = desk + self.url
            else:
                next_url = get_next_link(self.query.headers.get("link"))
                if not next_url:
                    raise StopIteration

            while True:
                self.query = r.get(
                    next_url,
                    auth=(config("API_KEY"), "X"),
                    timeout=60,
                )

                print(".", end="", flush=True)

                if self.query.status_code == 429:
                    retry_after = int(self.query.headers.get("Retry-After", "60"))
                    print(f"\nRate limited. Sleeping for {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue

                if self.query.status_code != 200:
                    print("\nFreshdesk returned a non-200 response.")
                    print("URL:", next_url)
                    print("Status:", self.query.status_code)
                    print("Content-Type:", self.query.headers.get("Content-Type"))
                    print("Body preview:", self.query.text[:500])
                    raise Exception("Freshdesk API request failed.")

                try:
                    self.memory = self.query.json()
                except Exception:
                    print("\nFreshdesk returned a response that was not valid JSON.")
                    print("URL:", next_url)
                    print("Status:", self.query.status_code)
                    print("Content-Type:", self.query.headers.get("Content-Type"))
                    print("Body preview:", self.query.text[:500])
                    raise

                self.count += 1
                break

        if not self.memory:
            raise StopIteration

        return self.memory.pop()
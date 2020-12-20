import lib
import databases

conn = databases.connect_and_create()                               
cur = conn.cursor()

def tickets():
    return lib.FreshdeskIterator("/api/v2/tickets?updated_since=2020-12-13T00:00:00Z&order_type=asc&order_by=created_at&per_page=100&page=1&include=description")

def conversations(ticket):
    ticket_id = ticket["id"]
    return lib.FreshdeskIterator(f"/api/v2/tickets/{ticket_id}/conversations")

def tags(ticket):
    return ticket["tags"]

for ticket in tickets():
    databases.save_ticket(cur, ticket)

    for conversation in conversations(ticket):
      databases.save_conversation(cur, conversation)

    for tag in tags(ticket):
      databases.save_tag(cur, ticket["id"], tag)
      
    conn.commit()
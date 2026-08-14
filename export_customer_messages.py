import sqlite3

import pandas as pd


conn = sqlite3.connect("tickets.db")

tickets = pd.read_sql(
    """
    SELECT
        tickets.id AS ticket_id,
        tickets.created_at AS ticket_created_at,
        tickets.subject,
        tickets.description_text AS initial_customer_message,
        tickets.priority,
        tickets.status,
        tickets.type,
        tickets.group_id,
        GROUP_CONCAT(tags.name, ', ') AS tags
    FROM tickets
    LEFT JOIN tags ON tickets.id = tags.ticket_id
    GROUP BY tickets.id
    """,
    conn,
)

conversations = pd.read_sql(
    """
    SELECT
        ticket_id,
        id AS conversation_id,
        body_text,
        incoming,
        private,
        created_at
    FROM conversations
    WHERE incoming = 1
      AND COALESCE(private, 0) != 1
      AND body_text IS NOT NULL
      AND TRIM(body_text) != ''
    ORDER BY ticket_id, created_at
    """,
    conn,
)

rows = []

for _, ticket in tickets.iterrows():
    tags = str(ticket.get("tags") or "")
    has_ai_first_response = "Onyx Reply" in tags

    initial_message = str(ticket.get("initial_customer_message") or "").strip()

    if initial_message:
        rows.append({
            "ticket_id": ticket["ticket_id"],
            "message_type": "initial_customer_message",
            "message_created_at": ticket["ticket_created_at"],
            "body_text": initial_message,
            "has_ai_first_response": has_ai_first_response,
            "tags": tags,
            "priority": ticket["priority"],
            "status": ticket["status"],
            "type": ticket["type"],
            "group_id": ticket["group_id"],
            "subject": ticket["subject"],
        })

    ticket_conversations = conversations[
        conversations["ticket_id"] == ticket["ticket_id"]
    ]

    customer_reply_index = 1

    for _, conversation in ticket_conversations.iterrows():
        rows.append({
            "ticket_id": ticket["ticket_id"],
            "message_type": "customer_reply",
            "message_created_at": conversation["created_at"],
            "body_text": conversation["body_text"],
            "has_ai_first_response": has_ai_first_response,
            "tags": tags,
            "priority": ticket["priority"],
            "status": ticket["status"],
            "type": ticket["type"],
            "group_id": ticket["group_id"],
            "subject": ticket["subject"],
            "customer_reply_index": customer_reply_index,
        })

        customer_reply_index += 1

output = pd.DataFrame(rows)
output.to_csv("customer_messages_for_sentiment.csv", index=False)

print(f"Exported {len(output)} customer messages.")
print("Saved customer_messages_for_sentiment.csv")
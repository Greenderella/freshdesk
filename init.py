import requests
from decouple import config
import sqlite3

#function that transforms from json -> tuple
def ticket_content(json):
    return (json["description"],json["description_text"],json["due_by"],json["fr_due_by"],json["fr_escalated"],json["group_id"],json["id"],json["is_escalated"],json["priority"],json["product_id"],json["requester_id"],json["responder_id"],json["source"],json["spam"],json["status"],json["subject"],json["type"],json["created_at"],json["updated_at"])

#############

r = requests.get('https://bitwarden.freshdesk.com/api/v2/tickets?include=description', auth=(config('API_KEY'), 'X'))

tickets = r.json()

conn = sqlite3.connect('tickets.db')

cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS tickets (description TEXT,description_text TEXT,due_by INTEGER,fr_due_by INTEGER,fr_escalated TEXT,group_id TEXT,id INTEGER NOT NULL PRIMARY KEY,is_escalated TEXT,priority INTEGER,product_id INTEGER,requester_id INTEGER,responder_id INTEGER,source TEXT,spam TEXT,status TEXT,subject TEXT,type INTEGER,created_at INTEGER,updated_at INTEGER)")

cur.execute("CREATE TABLE IF NOT EXISTS tags (ticket_id INTEGER NOT NULL, name TEXT)")

for ticket in tickets:
    cur.execute("INSERT INTO tickets(description,description_text,due_by,fr_due_by,fr_escalated,group_id,id,is_escalated,priority,product_id,requester_id,responder_id,source,spam,status,subject,type,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", ticket_content(ticket))
    for tag in ticket["tags"]:
        cur.execute("INSERT INTO tags(ticket_id, name) VALUES (?,?)", (ticket["id"],tag))   
        
conn.commit()
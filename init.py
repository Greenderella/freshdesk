import requests as r
from decouple import config
import sqlite3
import re

#function that transforms from json -> tuple
def ticket_content(json):
    return (json["description"],json["description_text"],json["due_by"],json["fr_due_by"],json["fr_escalated"],json["group_id"],json["id"],json["is_escalated"],json["priority"],json["product_id"],json["requester_id"],json["responder_id"],json["source"],json["spam"],json["status"],json["subject"],json["type"],json["created_at"],json["updated_at"])

#query the API and format the results as json

desk = 'https://bitwarden.freshdesk.com'

query = r.get(desk+"/api/v2/tickets?updated_since=2020-12-01T00:00:00Z&order_type=asc&order_by=created_at&per_page=100&page=1&include=description", auth=(config('API_KEY'), 'X'))

tickets = query.json()

#create tables

conn = sqlite3.connect('tickets.db')

cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS tickets (description TEXT,description_text TEXT,due_by INTEGER,fr_due_by INTEGER,fr_escalated TEXT,group_id TEXT,id INTEGER NOT NULL PRIMARY KEY,is_escalated TEXT,priority INTEGER,product_id INTEGER,requester_id INTEGER,responder_id INTEGER,source TEXT,spam TEXT,status TEXT,subject TEXT,type INTEGER,created_at INTEGER,updated_at INTEGER)")

cur.execute("CREATE TABLE IF NOT EXISTS tags (ticket_id INTEGER NOT NULL, name TEXT)")

#insert tickets

stopper = False #prepping to exit the loop
count = 1 #prepping a counter for a printer summary later on

while stopper == False:
    try:
        query.headers['link'] #check if there are more pages available
    except:
        print("Total ", count," pages totalling", len(tickets)," Total tickets")
        stopper = True #if no more pages, exit loop and print a summary of what was retrieved
    else:
        l = re.search(r'<(.*?)>', query.headers['link']).group(1) #grab the next page's URL from the original response
        query = r.get(l, auth=(config('API_KEY'), 'X')) #query again using the new URL
        print('.', end='', flush=True)
        tickets = tickets + query.json() #add the new set of results to the existing list
        count += 1 #carry on

for ticket in tickets:
    try:
        cur.execute("INSERT INTO tickets(description,description_text,due_by,fr_due_by,fr_escalated,group_id,id,is_escalated,priority,product_id,requester_id,responder_id,source,spam,status,subject,type,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", ticket_content(ticket))
        for tag in ticket["tags"]:
            cur.execute("INSERT INTO tags(ticket_id, name) VALUES (?,?)", (ticket["id"],tag))
    except:
        print("Ticket with ID  ", ticket["id"]," was already in the DB, skipping")
    
conn.commit()
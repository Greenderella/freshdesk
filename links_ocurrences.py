import sqlite3
import re
from url_extract import *

conn = sqlite3.connect('tickets.db')
cur = conn.cursor()
cur.execute('SELECT body FROM conversations')
list_of_bodies = cur.fetchall() #list of tuple

ocurrences = {}

for body in list_of_bodies:
    links = extract_bw_url(body[0])
    for link in links:
        ocurrences[link] = ocurrences.get(link, 0) + 1

print(ocurrences)

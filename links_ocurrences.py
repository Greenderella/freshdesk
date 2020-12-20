import sqlite3
import re
from url_extract import *
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

conn = sqlite3.connect('tickets.db')
cur = conn.cursor()
cur.execute('SELECT body FROM conversations')
list_of_bodies = cur.fetchall() #list of tuple

ocurrences = {}

for body in list_of_bodies:
    links = extract_bw_url(body[0])
    for link in links:
        ocurrences[link] = ocurrences.get(link, 0) + 1

a = sorted(ocurrences.items(), key=lambda item: item[1])
a.reverse()
b = dict(a[:30])

#########graph#########

# colors
color = cm.viridis_r(np.linspace(.4, .8, 30))
bars = plt.bar(b.keys(), b.values(), color=color)

# ocurrence number on each bar
heights = [0, 25, 50]
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x(), yval + .005, yval)

# labels
plt.title('Most Shared links from our Help Center')
plt.ylabel('Ocurrences')
plt.xlabel('Links')
plt.xticks(rotation=90)

plt.savefig('images/Most Shared links from our Help Center.png', dpi=300, bbox_inches='tight')
plt.show()



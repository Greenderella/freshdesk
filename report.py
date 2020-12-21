import pandas as pd
import seaborn as sns
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

conn = sqlite3.connect('tickets.db')

# priority histogram
df = pd.read_sql("SELECT priority FROM tickets", conn)
sns.catplot(x="priority", kind="count", palette="viridis", data=df)

plt.title('Amount of Tickets by Priority', fontsize=16)
plt.xlabel('Priority', fontsize=14)
plt.ylabel('Number of tickets', fontsize=14)

plt.savefig('images/Historic Amount of Tickets by Priority.png', dpi=500, bbox_inches='tight')

# tags histogram
df = pd.read_sql("SELECT name, count(name) FROM tags GROUP BY name ORDER BY count(name) DESC", conn)
sns.barplot(x="name", y="count(name)", palette="viridis", data=df)

plt.title('Amount of Tickets by Tag', fontsize=16)
plt.xlabel('Tag', fontsize=14)
plt.ylabel('Number of tickets', fontsize=14)
plt.xticks(rotation=90)

plt.savefig('images/Historic amount of tickets by Tag.png', dpi=500, bbox_inches='tight')
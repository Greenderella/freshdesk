import pandas as pd
import seaborn as sns
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

conn = sqlite3.connect('tickets.db')

# priority histogram
df = pd.read_sql("SELECT priority FROM tickets", conn)
sns.catplot(x="priority", kind="count", palette="ch:.25", data=df)

plt.title('Historic Amount of Tickets by Priority', fontsize=16)
plt.xlabel('Priority', fontsize=14)
plt.ylabel('Number of tickets', fontsize=14)

plt.savefig('images/Historic Amount of Tickets by Priority.png', dpi=500, bbox_inches='tight')
plt.show()

# tags histogram
df = pd.read_sql("SELECT name FROM tags", conn)
sns.catplot(x="name", kind="count", palette="ch:.25", data=df)

plt.title('Historic Amount of Tickets by Tag', fontsize=16)
plt.xlabel('Tag', fontsize=14)
plt.ylabel('Number of tickets', fontsize=14)
plt.xticks(rotation=90)

plt.savefig('images/Historic amount of tickets by Tag.png', dpi=500, bbox_inches='tight')
plt.show()

# wordcloud histogram
df = pd.read_sql("SELECT description_text FROM tickets JOIN tags ON tickets.id = tags.ticket_id WHERE tags.name = 'Technical Support'", conn)
text = " ".join(ticket for ticket in df.description_text)
#print ("There are {} words in the combination of all review.".format(len(text)))

stopwords = set(STOPWORDS)
stopwords.update(["Bitwarden", "password", "Technical", "Thank", "Subject", "account", "Thanks", "Support", "Please", "will", "Hi", "new", "Hello", "Inc", "use", "know", "still", "need", "Product", "Sales", "Kind", "regards", "see", "let", "Best", "regard", "Facebook"])

wordcloud = WordCloud(stopwords=stopwords, background_color="white", width=1600, height=800).generate(text)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")

plt.savefig('images/Wordcloud for tag = Technical Support.png', dpi=500, bbox_inches='tight')
plt.show()
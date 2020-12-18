import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sqlite3
from nltk.corpus import stopwords

conn = sqlite3.connect('tickets.db')
df = pd.read_sql("SELECT priority FROM tickets", conn)

#histogram

sns.catplot(x="priority", kind="count", palette="ch:.25", data=df)
plt.title('Historic amount of tickets by Priority', fontsize=16)
plt.xlabel('Priority', fontsize=14)
plt.ylabel('Frequency', fontsize=14)

plt.show()

#tags histogram

df = pd.read_sql("SELECT name FROM tags", conn)

sns.catplot(x="name", kind="count", palette="ch:.25", data=df)
plt.title('Historic amount of tickets by Tag', fontsize=16)
plt.xlabel('Tag', fontsize=14)
plt.ylabel('Frequency', fontsize=14)

plt.show()

#wordcloud histogram

df = pd.read_sql("select description_text from tickets", conn)

text_2 = " ".join(ticket for ticket in df.description_text)
print ("There are {} words in the combination of all review.".format(len(text_2)))

stopwords = set(STOPWORDS)
stopwords.update(["Bitwarden", "password", "Technical", "Thank", "Subject", "account", "Thanks", "Support", "Please", "will", "Hi", "new", "Hello", "Inc", "use", "know", "still", "need", "Product", "Sales", "Kind", "regards", "see", "let", "Best", "regard"])

wordcloud = WordCloud(stopwords=stopwords, background_color="white").generate(text_2)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()
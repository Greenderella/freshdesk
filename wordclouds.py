import pandas as pd
import seaborn as sns
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

conn = sqlite3.connect('tickets.db')

stopwords = set(STOPWORDS)
stopwords.update(["Bitwarden", "password", "Technical", "Thank", "Subject", "account", "Thanks", "Support", "Please", "will", "Hi", "new", "Hello", "Inc", "use", "know", "still", "need", "Product", "Sales", "Kind", "regards", "see", "let", "Best", "regard", "Facebook", "zwnj", "nbsp", "user", "email", "twitter", "Facebook", "now", "u","https", "Reddit"])

def wordcloud_by_tag(tag): 
    df = pd.read_sql(f"SELECT description_text FROM tickets JOIN tags ON tickets.id = tags.ticket_id WHERE tags.name = '{tag}' AND tickets.spam=0", conn)
    text = " ".join(ticket for ticket in df.description_text)

    wordcloud = WordCloud(stopwords=stopwords, background_color="white", width=1600, height=800).generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    tag = tag.replace(":", "_")
    plt.savefig(f'images/Wordcloud for tag {tag}.png', dpi=500, bbox_inches='tight')

wordcloud_by_tag('Technical Support')
wordcloud_by_tag('Direct')
wordcloud_by_tag('Org: Enterprise')
wordcloud_by_tag('Premium')
wordcloud_by_tag('Other')
wordcloud_by_tag('Sales')

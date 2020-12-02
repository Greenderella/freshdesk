import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sqlite3

conn = sqlite3.connect('tickets.db')
df = pd.read_sql("SELECT priority FROM tickets", conn)

#histogram
sns.catplot(x="priority", kind="count", palette="ch:.25", data=df)
plt.title('Historic amount of tickets by Priority', fontsize=16)
plt.xlabel('Priority', fontsize=14)
plt.ylabel('Frequency', fontsize=14)

plt.show()
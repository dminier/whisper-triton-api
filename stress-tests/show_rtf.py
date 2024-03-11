import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('rtf_report.txt', sep=";")


data['date'] = pd.to_datetime(data['date'])

data = data.sort_values(by='date')

# Tracer le graphique
plt.figure(figsize=(10, 6))
plt.plot(data['date'], data['rtf'], marker='o', linestyle='-')
plt.title('RTF')
plt.xlabel('Date')
plt.ylabel('RTF')
plt.grid(True)
plt.savefig("rtf.png")
plt.show()
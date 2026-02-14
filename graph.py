import pandas as pd
# import plotly.express as px
import matplotlib.pyplot as plt

df = pd.read_csv('data/graph/train-loss.csv')
train_series = df['Train Loss'].tolist()
valid_series = df['Validation Loss'].tolist()

# fig = px.line(df, y='Validation Loss', title='Train')
# fig.show()

plt.plot(train_series)
plt.plot(valid_series)

plt.show()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('/home/clphan/thesis/processed_dataset/wc_dataset_processed.csv', usecols=[1, 2, 3])
# df['event_count'].plot(figsize=(20,10))

# plt.plot(df['event_time'], df['event_count'])

# Count number of data contains zero value
df[df == 0] = pd.NaT  # replace zeros with NaT (not a time)
df = df.fillna(method='bfill')

delta_change = []
for index, row in df.iterrows():
    # case data suddenly change
    if index > 1:
        delta_change = delta_change.append((df['event_count'][index - 1] - row['event_count'])/ df['event_count'][index - 1]*100)
        # delta_change = (df['event_count'][index - 1] - row['event_count'])/ df['event_count'][index - 1]*100
        # print(delta_change)


# # zero_bytes = (df['sum_bytes'] < 10000).sum()
# print(zero_count)
# plt.plot(delta_change)

# plt.show()
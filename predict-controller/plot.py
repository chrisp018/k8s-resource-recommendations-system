import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('wc_dataset_processed.csv')

# Plot for event_count
plt.plot(df['event_time'], df['event_count'])
plt.xlabel('Time')
plt.ylabel('Event Count')
plt.title('Event Count vs Time')

# Plot for num_match_event
plt.figure()   # This creates a new plot
plt.plot(df['event_time'], df['num_match_event'], color='red')
plt.xlabel('Time')
plt.ylabel('Num Match Event')
plt.title('Num Match Event vs Time')

# Show the plots
plt.show()
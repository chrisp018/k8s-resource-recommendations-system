import pandas as pd
import matplotlib.pyplot as plt

# Load the data into a Pandas dataframe
data = pd.read_csv("wc_dataset_processed_extract.csv", parse_dates=["event_time"])

# Set the event_time column as the dataframe index
data.set_index("event_time", inplace=True)

# Set the end datetime to plot the data up to
end_datetime = pd.to_datetime("1998-04-30 23:30:00")

# Filter the data to the desired range
data = data.truncate(before=data.index.min(), after=end_datetime)

# Create a new figure and axis
fig, ax = plt.subplots()

# Plot the event_count column as a line graph
ax.plot(data.index, data["event_count"], label="Event Count")

# Set the axis labels and legend
ax.set_xlabel("Time")
ax.set_ylabel("Event Count")
ax.legend()

# Display the plot
plt.show()

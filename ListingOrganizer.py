import pandas as pd
import numpy as np
import googlemaps
from geopy.distance import geodesic
import threading
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()
api_key = os.getenv('API_KEY')
# Use your own Google Maps API key here
gmaps = googlemaps.Client(key=api_key)
# Geocode Peterborough, Ontario
peterborough = gmaps.geocode('Peterborough, Ontario')[0]['geometry']['location']

# Function to calculate distance to Peterborough
def distance_to_peterborough(location):
    try:
        geocoded_location = gmaps.geocode(location)[0]['geometry']['location']
        return geodesic((peterborough['lat'], peterborough['lng']), (geocoded_location['lat'], geocoded_location['lng'])).miles
    except:
        return None

# Function to apply distance_to_peterborough to a series of locations
def apply_distance_to_series(locations, output, index):
    output[index] = locations.apply(distance_to_peterborough)

# Read the Excel file
df = pd.read_excel("job_listings.xlsx")

# Create a list of columns excluding 'url'
columns_except_url = [col for col in df.columns if col != 'url']

# Drop duplicates based on the subset of columns
df.drop_duplicates(subset=columns_except_url, inplace=True)

# Clean up and organize the data if needed
# For example, you can remove leading/trailing whitespaces from all columns
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Add a new column that indicates whether the job is remote or hybrid
df['Remote or Hybrid'] = df['Location'].str.contains('remote|hybrid', case=False) | df['Description'].str.contains('remote|hybrid', case=False)

# Split the DataFrame into chunks
chunks = np.array_split(df['Location'], 10)

# Create a list to hold the output
output = [None] * 10

# Create and start a thread for each chunk
threads = []
for i in range(10):
    thread = threading.Thread(target=apply_distance_to_series, args=(chunks[i], output, i))
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()

# Concatenate the output and add it to the DataFrame
df['Distance to Peterborough'] = pd.concat(output)

# Sort by whether the job is remote or hybrid, and then by distance to Peterborough
df.sort_values(by=['Remote or Hybrid', 'Distance to Peterborough'], ascending=[False, True], inplace=True)

# Save the cleaned data to a new Excel file
df.to_excel("cleaned_job_listings.xlsx", index=False)

print("Data cleaning and organization complete!")
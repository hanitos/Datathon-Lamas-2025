import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.map import Icon

# Sample DataFrame
data = {
    'City': ['New York', 'Los Angeles', 'Chicago', 'New York', 'Los Angeles'],
    'Latitude': [40.7128, 34.0522, 41.8781, 40.7128, 34.0522],
    'Longitude': [-74.0060, -118.2437, -87.6298, -74.0060, -118.2437],
    'Category': ['A', 'B', 'A', 'C', 'C'],
    'Value': [10, 20, 30, 40, 50]  # Example column to determine marker color
}
df = pd.DataFrame(data)

# Function to determine marker color based on value
def get_marker_color(value):
    if value < 15:
        return 'green'
    elif value < 25:
        return 'orange'
    else:
        return 'red'

# Streamlit app
st.title('Interactive Map with Selections')

# Dropdown for selecting city
selected_city = st.selectbox('Select City', df['City'].unique())

# Filter categories based on selected city
filtered_categories = df[df['City'] == selected_city]['Category'].unique()

# Dropdown for selecting category based on selected city
selected_category = st.selectbox('Select Category', filtered_categories)

# Filter DataFrame based on selections
filtered_df = df[(df['City'] == selected_city) & (df['Category'] == selected_category)]

# Create Folium map
m = folium.Map(location=[filtered_df['Latitude'].mean(), filtered_df['Longitude'].mean()], zoom_start=5)

# Add markers to the map with colors based on 'Value' column
for _, row in filtered_df.iterrows():
    marker_color = get_marker_color(row['Value'])
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        radius=row['Value'] / 10,
        popup=row['City'],
        icon=Icon(color=marker_color)
    ).add_to(m)

# Display the map in Streamlit
st_folium(m, width=700, height=500)

from functools import reduce
import streamlit as st
import folium
from pyproj import Proj, transform
from streamlit_folium import st_folium
from folium.map import Icon
import pandas as pd

def create_key(df, columns, seperator='_'):
    '''
    returns a df column with concatenated columns value
    example:df['key']=create_key(df,[col1,col2,col3],seperator=';')
    '''
    return reduce(lambda x1,x2:x1+seperator+x2,[df[c].astype(str).str.upper() for c in columns])

# Function to determine marker color based on value
def get_marker_color(value):
    if value <= 1:
        return 'green'
    elif value <= 2:
        return 'orange'
    else:
        return 'red'

def itm_to_wgs84(x, y):
    itm_proj = Proj(init='epsg:2039')  # Israel TM Grid
    wgs84_proj = Proj(init='epsg:4326')
    lon, lat = transform(itm_proj, wgs84_proj, x, y)
    return lon, lat#f'{lat},{lon}'

def convert_coord(df,coord_col='coord'):
    unique_coords = df[[coord_col]].drop_duplicates().reset_index(drop=True)
    coord_global = []
    for i in range(len(unique_coords)):
        lon,lat = itm_to_wgs84(*unique_coords.loc[i,coord_col].split(','))
        coord_global.append(f'{lat},{lon}')
    unique_coords['global_coord'] = coord_global
    df = pd.merge(df,unique_coords,on='coord',how='inner')
    return df

# Function to determine marker icon based on shape
def get_marker_icon(shape):
    if shape == 'circle':
        return 'circle'
    elif shape == 'square':
        return 'square'
    elif shape == 'triangle':
        return 'triangle'
    else:
        return 'info-sign'  # Default icon

# from folium.features import CustomIcon
# def get_custom_icon(shape):
#     if shape == 'cross':
#         return CustomIcon('path/to/cross_icon.png', icon_size=(30, 30))
#     elif shape == 'star':
#         return CustomIcon('path/to/star_icon.png', icon_size=(30, 30))
#     else:
#         return CustomIcon('path/to/default_icon.png', icon_size=(30, 30))


df = pd.read_csv(r'C:\Python_projects\MyCode\datathone\data\דאטה תאונות דרכים.csv')
df = df.loc[df['X'].notnull() & df['Y'].notnull()]
if 'coord' not in df.columns:
    df['coord'] = create_key(df, ['X','Y'], seperator=',')
if 'global_coord' not in df.columns:
    df = convert_coord(df)
df['SHNAT_TEU'] = df['SHNAT_TEU'].astype(str)
year_selector = sorted(df['SHNAT_TEU'].dropna().unique().tolist())
year_selector.insert(0, 'All')


# Streamlit app
st.title('Interactive Map with Selections')
# Dropdown for selecting city
selected_year = st.selectbox('Select Year', year_selector,index=0)

# optional for additional filters
# # Filter categories based on selected city
# filtered_categories = df[df['City'] == selected_city]['Category'].unique()
#
# # Dropdown for selecting category based on selected city
# selected_category = st.selectbox('Select Category', filtered_categories,)

# Filter DataFrame based on selections
filtered_df = df[['SHNAT_TEU','coord','HUMRAT_TEUNA']].dropna()
if selected_year != 'All':
    filtered_df = filtered_df[(filtered_df['SHNAT_TEU'] == selected_year)]# & (df['Category'] == selected_category)]
g = filtered_df.groupby('coord').agg({'coord':'size','HUMRAT_TEUNA':'mean'}).dropna().rename(columns={'coord': 'size'}).sort_values(by='size').reset_index()
# max_count = g['size'].max()

# Create Folium map
m = folium.Map(location=[31.5161, 34.8516], zoom_start=7.4)  # Y & X

# Add markers to the map with colors and shapes based on 'Value' and 'Shape' columns
for i in range(len(g)):
    row = g.iloc[i]
    marker_color = get_marker_color(row['HUMRAT_TEUNA'])
    # marker_icon = get_marker_icon(row['Shape'])
    coords = [float(c) for c in row['global_coord'].split(',')]
    folium.CircleMarker(
        location=[coords[0],coords[1]],
        radius=row['size'] / 10,  # Adjust the divisor to control the size scaling
        color=marker_color,
        fill=True,
        fill_color=marker_color,
        fill_opacity=0.6
    ).add_to(m)

# Display the map in Streamlit
st_folium(m, width=800, height=500)

# Sidebar to display information about the selected row
# st.sidebar.title('Selected Row Information')
# if not filtered_df.empty:
#     selected_row = filtered_df.iloc[0]  # Assuming the first row is selected for simplicity
#     st.sidebar.write(f"**City:** {selected_row['City']}")
#     st.sidebar.write(f"**Category:** {selected_row['Category']}")
#     st.sidebar.write(f"**Value:** {selected_row['Value']}")
#     st.sidebar.write(f"**Info:** {selected_row['Info']}")
# else:
#     st.sidebar.write("No data available for the selected options.")

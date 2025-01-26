from functools import reduce
import folium
from pyproj import Proj, transform
import pandas as pd
import chardet
from shiny import App, render, ui

# Set pandas to display all columns permanently
pd.set_option('display.max_columns', None)

# Helper functions
def create_key(df, columns, seperator='_'):
    return reduce(lambda x1, x2: x1 + seperator + x2, [df[c].astype(str).str.upper() for c in columns])

def get_marker_color(value, severity_selector):
    if value == severity_selector[0]:
        return 'red'
    elif value == severity_selector[1]:
        return 'orange'
    else:
        return 'green'

def itm_to_wgs84(x, y):
    itm_proj = Proj(init='epsg:2039')  # Israel TM Grid
    wgs84_proj = Proj(init='epsg:4326')
    lon, lat = transform(itm_proj, wgs84_proj, x, y)
    return lon, lat

def convert_coord(df, coord_col='coord'):
    unique_coords = df[[coord_col]].drop_duplicates().reset_index(drop=True)
    coord_global = []
    for i in range(len(unique_coords)):
        lon, lat = itm_to_wgs84(*unique_coords.loc[i, coord_col].split(','))
        coord_global.append(f'{lat},{lon}')
    unique_coords['global_coord'] = coord_global
    df = pd.merge(df, unique_coords, on='coord', how='inner')
    return df

def create_df():
    # Load data
    data_file = "shared_data/דאטה תאונות דרכים.csv"
    with open("shared_data/דאטה תאונות דרכים.csv", "rb") as file:
        result = chardet.detect(file.read())

    df = pd.read_csv(data_file, encoding=result['encoding'])
    df = df.loc[df['X'].notnull() & df['Y'].notnull()]
    if 'coord' not in df.columns:
        df['coord'] = create_key(df, ['X', 'Y'], seperator=',')
    if 'global_coord' not in df.columns:
        df = convert_coord(df)
        df.to_csv(data_file, index=False, encoding='cp1255')

    df['SHNAT_TEU'] = df['SHNAT_TEU'].astype(int).astype(str)
    year_selector = sorted(df['SHNAT_TEU'].dropna().unique().tolist(), reverse=True)
    year_selector.insert(0, 'כל השנים')
    severity_selector = ['קטלנית', 'קשה', 'קלה', 'כל התאונות']

    #load population data
    df_population = pd.read_excel("shared_data/population 2022.xlsx")

    '''
    # Perform a left join to add LocNameHeb to df
    df = df.merge(df_population[['LocalityCode', 'LocNameHeb']],
                    left_on='SEMEL_YISHUV',
                    right_on='LocalityCode',
                    how='left')

    # Drop LocalityCode from df
    df = df.drop(columns=['LocalityCode'])
    '''

    return df, year_selector, severity_selector

# Function to create a right-aligned input element
def right_aligned_input(input_element):
    return ui.div(
        ui.div(input_element, style="text-align: right; width: 100%;"),  # Right-aligned label
        style="margin-bottom: 15px;"  # Add spacing between inputs
    )

# Shiny UI
def create_ui(df):
    return ui.page_sidebar(
        ui.sidebar(
                ui.input_select("year", "שנת תאונה", year_selector, selected=year_selector[1]),
                ui.input_select("severity", "חומרת תאונה", severity_selector, selected=severity_selector[-1]),
                ui.input_slider("size", "כמות תאונות מינימלית למיקום", 1, 20, 2),
                ui.output_text_verbatim("sidebar_details"),
                ui.input_action_button("save", "Save Map and Data"),
                #ui.input_select("city","בחר/י עיר",choices=df["LocNameHeb"].tolist(),selected=None),
                position="right"
        ),
        ui.h2("ישראל - מפת תאונות", align="right" ,position="right"),
        ui.output_ui("map")
    )

#server logic
def server(input, output, session):
    @output
    @render.ui
    def map():
        selected_year = input.year()
        selected_severity = input.severity()
        selected_size = input.size()

        if selected_year != 'כל השנים':
            g = df[df['SHNAT_TEU'] == selected_year]
        else:
            g = df

        g = g.groupby('global_coord').agg(
            size=('global_coord', 'size'),
            HUMRAT_TEUNA=('HUMRAT_TEUNA', 'mean'),
            num_nifgaim=('num_nifgaim', 'sum'),
            KLE_REHEV_HUZNU=('KLE_REHEV_HUZNU', 'sum')
        ).reset_index()

        severity_bounds = [1.7, 2, 2.5]
        g.loc[g['HUMRAT_TEUNA'] <= severity_bounds[0], 'severity'] = severity_selector[0]
        g.loc[(g['HUMRAT_TEUNA'] > severity_bounds[0]) & (g['HUMRAT_TEUNA'] <= severity_bounds[1]), 'severity'] = severity_selector[1]
        g.loc[g['HUMRAT_TEUNA'] > severity_bounds[1], 'severity'] = severity_selector[2]

        if selected_severity != 'כל התאונות':
            g = g[g['severity'] == selected_severity]

        g = g[g['size'] >= selected_size]

        #m = folium.Map(location=[31.5161, 34.8516], zoom_start=7.4)
        m = folium.Map(location=[30.6, 34.8516], zoom_start=7.4)
        for i, row in g.iterrows():
            coords = [float(c) for c in row['global_coord'].split(',')]
            marker_color = get_marker_color(row['severity'], severity_selector)
            popup_text = f"""
                מספר תאונות: {row['size']}<br>
                מספר נפגעים: {row['num_nifgaim']}<br>
                מספר כלי רכב מעורבים: {row['KLE_REHEV_HUZNU']}
            """
            folium.CircleMarker(
                location=coords,
                radius=row['size'] / 2,
                color=marker_color,
                fill=True,
                fill_color=marker_color,
                fill_opacity=0.6,
                popup=folium.Popup(popup_text, max_width=300)
            ).add_to(m)

        return ui.tags.iframe(srcdoc=m._repr_html_(), width="100%", height="500")

    @output
    @render.text
    def sidebar_details():
        selected_year = input.year()
        selected_severity = input.severity()
        selected_size = input.size()

        if selected_year != 'כל השנים':
            filtered_df = df[df['SHNAT_TEU'] == selected_year]
        else:
            filtered_df = df

        total_accidents = filtered_df.shape[0]
        total_injuries = filtered_df['num_nifgaim'].sum()
        total_vehicles = filtered_df['KLE_REHEV_HUZNU'].sum()

        return f"""
        תאונות: {total_accidents}
        נפגעים: {total_injuries}
        כלי רכב: {total_vehicles}
        """



if __name__ == "__main__":
    df, year_selector, severity_selector = create_df()

    # Create the UI using the dataframe
    app_ui = create_ui(df)
    app = App(app_ui, server)
    app.run()
from shiny import App, render, ui
import pandas as pd
from plotnine import ggplot, aes, geom_bar, geom_histogram, theme, element_text, labs, coord_flip, scale_fill_manual, \
    scale_x_discrete
from bidi.algorithm import get_display  # For RTL text correction
import numpy as np

# Set pandas to display all columns permanently
pd.set_option('display.max_columns', None)

# Mapping of values to display labels
occupation_dict = {
    "Mediation" : "תיווך",
    "Social" : "עבודה סוציאלית",
    "Lawyer": "עריכת דין",
    "Accounting" : "ראיית חשבון",
    "Architect" : "הנדסה ואדריכלות",
    "Paramedical" : "מקצועות פרה-רפואיים",
    "psychologist" : "פסיכולוגיה",
    "Pharmacist" : "רוקחות",
    "Nursing" : "סיעוד",
    "Dentist" : "רפואה ורפואת שיניים"
}

def create_df():
    #load population data
    df_population = pd.read_excel("shared_data/population 2022.xlsx")
    df_population_grouped = df_population.groupby(['LocNameHeb', 'LocalityCode'])['pop_approx'].sum().reset_index()
    df_population_grouped['LocalityCode'] = df_population_grouped['LocalityCode'].astype(int)

    #load business licenses data
    df_business_licenses = pd.read_csv("shared_data/Business license 2022.csv")

    #merege dfs
    df_merged = pd.merge(df_population_grouped, df_business_licenses, left_on='LocalityCode', right_on='SEMEL_YESUV', how='inner')

    # Add percentage columns
    for occupation in occupation_dict.keys():
        df_merged[f"{occupation}_percent"] = (df_merged[occupation] / df_merged["pop_approx"]) * 100
        # max 2 digits after the point
        df_merged[f"{occupation}_percent"] = df_merged[f"{occupation}_percent"].round(2)

    return df_merged


'''
# Replace invalid values and convert columns to numeric
df_c.replace('. .', 0, inplace=True)
'''

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
            right_aligned_input(
                ui.input_select(
                    "occupation",
                    ":בחר/י מקצוע",
                    choices=occupation_dict,
                    selected=list(occupation_dict.keys())[0]
                )
            ),
            right_aligned_input(
                ui.input_select(
                    "city",
                    "בחר/י עיר",
                    choices=df["LocNameHeb"].tolist(),
                    selected=df["LocNameHeb"][0]
                )
            ),
            position='right'
        ),
        ui.output_plot("occupation_plot"),  # Plot for bar chart
        ui.output_plot("histogram_plot")   # Plot for histogram
    )


# Server logic
def server(input, output, session):
    @output
    @render.plot
    def occupation_plot():
        selected_occupation = input.occupation()
        selected_city = input.city()

        occupation_label = occupation_dict[selected_occupation]

        # Total sum calculations
        total_occupation_sum = df_main[selected_occupation].sum()
        total_population_sum = df_main['pop_approx'].sum()
        total_percentage = (total_occupation_sum / total_population_sum) * 100

        # Selected Name calculations
        selected_row = df_main[df_main['LocNameHeb'] == selected_city]
        selected_percentage = selected_row[selected_occupation+'_percent'].values[0]

        # Data for the plot
        categories = [get_display(f'{selected_city}'), get_display('אחוזים ארציים')]
        percentages = [selected_percentage, total_percentage]
        plot_data = pd.DataFrame({'Category': categories, 'Percentage': percentages})


        # Create the plot using plotnine
        p = (
            ggplot(plot_data, aes(x='Category', y='Percentage', fill='Category'))
            + geom_bar(stat='identity', show_legend=False)
            + labs(
                title=get_display(f"ניתוח אחוזים עבור {occupation_label}"),
                y=get_display("%"),
                x=""
            )
            + theme(axis_text_x=element_text(rotation=0, ha='center'),
                    axis_text_y=element_text(ha='right'),
                    plot_title=element_text(ha='center'))
            + coord_flip()  # Flip the coordinates for better visualization
        )

        return p


    @output
    @render.plot
    def histogram_plot():
        selected_occupation = input.occupation()

        # Create the histogram using plotnine
        p = (
            ggplot(df_main, aes(x=selected_occupation+"_percent", fill=(df_main["LocNameHeb"] == input.city())))
            + geom_histogram(
                bins = 10,
                color = 'black',
                alpha=0.7,
                show_legend = False
            )
            + labs(
                title=get_display(f"היסטוגרמה עבור {occupation_dict[selected_occupation]}"),
                x=get_display("%"),
                y=get_display("תדירות")
            )
            + theme(
                axis_text_x=element_text(rotation=0, ha='center', size=10),
                axis_text_y=element_text(ha='right', size=10),
                plot_title=element_text(ha='center', size=14),
            )
        )


        return p




if __name__ == "__main__":
    df_main = create_df()
    print(df_main.info())

    # Create the UI using the dataframe
    app_ui = create_ui(df_main)

    # Create Shiny app
    app = App(app_ui, server)

    app.run()

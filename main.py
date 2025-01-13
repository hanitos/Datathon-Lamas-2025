from shiny import App, render, ui
import pandas as pd
import matplotlib.pyplot as plt

# Set pandas to display all columns permanently
pd.set_option('display.max_columns', None)

# Load the Excel file into a DataFrame
df = pd.read_excel("data/business_licenses_2022.xlsx", skiprows=6, nrows=79)
# Assign custom column names
df.columns = [
"Tivoch(women)",
"Tivoch(men)",
"Tivoch(total)",

    "social_work(women)",
    "social_work(men)",
    "social_work(total)",

    "lawyer(women)",
"lawyer(men)",
"lawyer(total)",

"accounting(women)",
"accounting(men)",
"accounting(total)",

    "הנדסה ואדריכלות (סהכ)",
    "הנדסה ואדריכלות (גברים)",
    "הנדסה ואדריכלות (נשים)",

    "מקצועות פרה-רפואיים (סהכ)",
    "מקצועות פרה-רפואיים (גברים)",
    "מקצועות פרה-רפואיים (נשים)",

    "פסיכולוגיה (סהכ)",
    "פסיכולוגיה (גברים)",
    "פסיכולוגיה (נשים)",

    "רוקחות (סהכ)",
    "רוקחות (גברים)",
    "רוקחות (נשים)",

    "סיעוד (סהכ)",
    "סיעוד (גברים)",
    "סיעוד (נשים)",

    "רפואה ורפואת שיניים (סהכ)",
    "רפואה ורפואת שיניים (גברים)",
    "רפואה ורפואת שיניים (נשים)",

    "Municipality_id",
    "Municipality"
]

category_dict = {
    "social_work" : "עבודה סוציאלית",
    "lawyer" : "עריכת דין",
    "pharmacy": "רוקחות",
    "psychology":"פסיכולוגיה"
}

# Define the Shiny app UI
app_ui = ui.page_fluid(
    ui.h2("בעלי רישיונות עיסוק בישובים ומועצות אזוריות 2022"),
    #ui.output_data_frame("table")
    ui.input_select("category", "Select a Category:", choices=category_dict),
    ui.output_plot("plot")
)

def load_population():
    df = pd.read_excel("data/population 2022.xlsx")
    df_grouped = df.groupby(['LocNameHeb','LocalityCode'])['pop_approx'].sum().reset_index()
    return df_grouped


def load_business_licenses():
    df = pd.read_excel("data/business_licenses_2022_test.xlsx")
    return df



# Define the server logic
def server(input, output, session):
    @output
    @render.plot
    def plot():
        # Filter data based on selected category
        selected_category = input.category()
        filtered_data = df_c[['LocNameHeb','LocalityCode','pop_approx', selected_category]]

        print('filtered_data.iloc[0, 1:]: ')
        print(filtered_data.iloc[0, 1:])

        # Create a bar plot
        fig, ax = plt.subplots()
        ax.bar(["Value1", "Value2", "Value3"], filtered_data.iloc[0, 1:])  # Plot values for the selected category
        ax.set_title(f"Values for Category {selected_category}")
        ax.set_ylabel("Values")

        return fig

# Create and run the app
app = App(app_ui, server)

if __name__ == "__main__":
    df_population = load_population()
    df_business_licenses = load_business_licenses()

    # Merge df_a and df_b on Code == id, keeping only matching rows
    df_c = pd.merge(df_population, df_business_licenses, left_on='LocalityCode', right_on='municipality_id', how='inner')

    print(df_c.head())

    app.run()

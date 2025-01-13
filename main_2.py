from shiny import App, render, ui
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
from bidi.algorithm import get_display  # For RTL text correction

# Configure Matplotlib for RTL and Hebrew support
rcParams['font.family'] = 'DejaVu Sans'  # Ensure a font supporting Hebrew is available
plt.rcParams['axes.unicode_minus'] = False  # Prevent issues with minus signs in plots

# Set pandas to display all columns permanently
pd.set_option('display.max_columns', None)

# Sample DataFrame
data = {
    'Name': ['A', 'B', 'C', 'D', 'E'],
    'pop': [2710, 31, 2400, 1020, 2600],
    'social_work': [115130, 35360, 73700, 22170, 110420],
    'lawyer': [163, 81, 38, 33, 140],
    'psychology': [210, 83, 168, 84, 169],
    'pharmacy': [32, 0, 13, 9, 44],
}
df = pd.DataFrame(data)

def load_population():
    df = pd.read_excel("data/population 2022.xlsx")
    df_grouped = df.groupby(['LocNameHeb','LocalityCode'])['pop_approx'].sum().reset_index()
    return df_grouped


def load_business_licenses():
    df = pd.read_excel("data/business_licenses_2022_test.xlsx")
    return df

df_population = load_population()
df_business_licenses = load_business_licenses()

# Merge df_a and df_b on Code == id, keeping only matching rows
df_c = pd.merge(df_population, df_business_licenses, left_on='LocalityCode', right_on='municipality_id', how='inner')

# Replace invalid values and convert columns to numeric
df_c.replace('. .', 0, inplace=True)

# Mapping of values to display labels
occupation_dict = {
    "social_work": "עבודה סוציאלית",
    "lawyer": "עריכת דין",
    "psychology": "פסיכולוגיה",
    "pharmacy": "רוקחות"
}

# Function to create a right-aligned input element
def right_aligned_input(input_element):
    return ui.div(
        ui.div(input_element, style="text-align: right; width: 100%;"),  # Right-aligned label
        style="margin-bottom: 15px;"  # Add spacing between inputs
    )

# Shiny UI
app_ui = (
    ui.page_sidebar(
        ui.sidebar(
            right_aligned_input(
                ui.input_select(
                    "occupation",
                    ":בחר/י מקצוע",
                    choices=occupation_dict,
                    selected="social_work"
                )
            ),
            right_aligned_input(
                ui.input_select(
                "city",
                "בחר/י עיר",
                    choices=df_c["LocNameHeb"].tolist(),
                    selected=df_c["LocNameHeb"][0]
                )
            ),
            position='right'
        ),
        ui.output_plot("occupation_plot")  # Main content: Matplotlib plot
    )
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
        total_occupation_sum = df_c[selected_occupation].sum()
        total_population_sum = df_c['pop_approx'].sum()
        total_percentage = (total_occupation_sum / total_population_sum) * 100

        # Selected Name calculations
        selected_row = df_c[df_c['LocNameHeb'] == selected_city]
        selected_occupation_value = selected_row[selected_occupation].values[0]
        selected_population_value = selected_row['pop_approx'].values[0]
        selected_percentage = (selected_occupation_value / selected_population_value) * 100

        # Create the plot using Matplotlib
        categories = [get_display('אחוזים ארציים'), get_display(f'{selected_city}')]
        percentages = [total_percentage, selected_percentage]

        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(categories, percentages, color=['blue', 'orange'])
        ax.set_title(get_display(f"ניתוח אחוזים עבור {occupation_label}"))
        ax.set_ylabel(get_display("%"), fontsize=12)

        # Set text alignment for RTL
        ax.tick_params(axis='x', labelrotation=0)
        plt.gca().invert_xaxis()  # Optional: reverse the x-axis if necessary

        # Add percentage values on top of each bar
        for bar, percentage in zip(bars, percentages):
            ax.text(
                bar.get_x() + bar.get_width() / 2,  # X-coordinate (center of the bar)
                bar.get_height(),                  # Y-coordinate (top of the bar)
                f"{percentage:.3f}%",             # Text to display
                ha='center',                      # Horizontal alignment
                va='bottom',                      # Vertical alignment
                fontsize=10,                      # Font size
                color='black'                     # Text color
            )

        # Return the plot
        return fig




# Create Shiny app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()


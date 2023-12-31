import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, ColorBar, HoverTool
from bokeh.transform import dodge
from bokeh.models import NumeralTickFormatter
from bokeh.models import Legend

# configuration of the page
st.set_page_config(layout="wide")

# Title
st.title("Ranking Comparison")

# Create a grouped bar chart using Bokeh
st.subheader("Only ONE csv file can be uploaded at a time.")

# Upload CSV file
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
filtered_df = None  # Initialize filtered_df outside the conditional block

if uploaded_file is not None:
    # Read the CSV file into a DataFrame
    df = pd.read_csv(uploaded_file, index_col=False, skiprows=0)

    # Dropping columns
    df = df.drop(columns=['Sno', 'Symbol', 'IndustryGroupRankLast6MonthAgo', 'PricePercentChangeYTD'])

    # Remove unwanted characters
    df['MarketCapital'] = df['MarketCapital'].replace({',': '', ' Cr': ''}, regex=True)

    # Convert 'MarketCapital' column to float
    df['MarketCapital'] = pd.to_numeric(df['MarketCapital'].str.replace(',', '').str.replace(' Cr', ''),
                                        errors='coerce')

    # Filter data based on market cap
    st.sidebar.header("Filter by Market Cap")
    min_market_cap = st.sidebar.number_input("Minimum Market Cap", float(df['MarketCapital'].min()),
                                            float(df['MarketCapital'].max()), float(df['MarketCapital'].min()))
    filtered_df = df[df['MarketCapital'] >= min_market_cap]

    # Convert 'IndustryGroupRankCurrent', 'IndustryGroupRankLastWeek', and 'IndustryGroupRankLast3MonthsAgo' columns to numeric
    filtered_df['IndustryGroupRankCurrent'] = pd.to_numeric(filtered_df['IndustryGroupRankCurrent'], errors='coerce')
    filtered_df['IndustryGroupRankLastWeek'] = pd.to_numeric(filtered_df['IndustryGroupRankLastWeek'],
                                                           errors='coerce')
    filtered_df['IndustryGroupRankLast3MonthAgo'] = pd.to_numeric(filtered_df['IndustryGroupRankLast3MonthAgo'],
                                                                 errors='coerce')

    # Filter based on the condition
    filtered_df = filtered_df[
        (filtered_df['IndustryGroupRankCurrent'] < filtered_df['IndustryGroupRankLastWeek']) &
        (filtered_df['IndustryGroupRankCurrent'] < filtered_df['IndustryGroupRankLast3MonthAgo'])]




# Create a grouped bar chart using Bokeh
st.subheader("Displaying Industry Group continuously down in last 3 month, last week & Current rank.")

# Add a checkbox to turn on/off text labels
show_labels = st.checkbox("Show Text Labels", value=True)

# Check if filtered_df is defined
if filtered_df is not None:
    # Rest of your code for creating the Bokeh chart and displaying the DataFrame
    source = ColumnDataSource(filtered_df)

    p = figure(x_range=filtered_df['IndustryGroupName'], plot_height=400, title="Industry Group Rankings",
               toolbar_location="above", tools="pan,box_zoom,reset,save")

    # Define the bars in the desired order
    p.vbar(x=dodge('IndustryGroupName', 0.0, range=p.x_range), top='IndustryGroupRankLast3MonthAgo', width=0.2,
           source=source, fill_color="#feb41f", line_color="#feb41f", legend_label="Last 3 Months Rank")

    p.vbar(x=dodge('IndustryGroupName', 0.2, range=p.x_range), top='IndustryGroupRankLastWeek', width=0.2,
           source=source, fill_color="#FF5733", line_color="#FF5733", legend_label="Last Week Rank")

    p.vbar(x=dodge('IndustryGroupName', 0.4, range=p.x_range), top='IndustryGroupRankCurrent', width=0.2,
           source=source, fill_color="#3377FF", line_color="#3377FF", legend_label="Current Rank")

    # Add text labels to the bars with smaller font size
    text_font_size = "8pt"

    # Add text labels to the bars
    if show_labels:
        p.text(x=dodge('IndustryGroupName', 0.0, range=p.x_range), y='IndustryGroupRankLast3MonthAgo',
               text='IndustryGroupRankLast3MonthAgo', text_align='center', text_baseline='bottom',
               source=source, y_offset=5, text_color="black", text_font_size=text_font_size)

        p.text(x=dodge('IndustryGroupName', 0.2, range=p.x_range), y='IndustryGroupRankLastWeek',
               text='IndustryGroupRankLastWeek', text_align='center', text_baseline='bottom',
               source=source, y_offset=5, text_color="black", text_font_size=text_font_size)

        p.text(x=dodge('IndustryGroupName', 0.4, range=p.x_range), y='IndustryGroupRankCurrent',
               text='IndustryGroupRankCurrent', text_align='center', text_baseline='bottom',
               source=source, y_offset=5, text_color="black", text_font_size=text_font_size)

    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None

    # Add hover tooltips
    hover = HoverTool()
    hover.tooltips = [("Industry Group", "@IndustryGroupName"),
                      ("Last 3 Months Rank", "@IndustryGroupRankLast3MonthAgo"),
                      ("Last Week Rank", "@IndustryGroupRankLastWeek"),
                      ("Current Rank", "@IndustryGroupRankCurrent")]
    p.add_tools(hover)

    # Create a custom legend
    legend: Legend = Legend(items=[(label, [glyph]) for glyph, label in
                                   zip(p.renderers, [item.label['value'] for item in p.legend.items])],
                            location="center")
    p.add_layout(legend, 'below')
    p.legend.orientation = "horizontal"

    # Remove the top right legend
    p.legend[0].visible = True

    # Show the bottom legend
    p.legend[1].visible = False

    # Format y-axis as integers
    p.yaxis[0].formatter = NumeralTickFormatter(format="0")

    # Customize chart appearance
    p.xaxis.major_label_orientation = "vertical"

    # Show the Bokeh chart with auto-fit to container width
    st.bokeh_chart(p, use_container_width=True)



    # Display filtered DataFrame
    grid = AgGrid(
        data=filtered_df,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW
    )
else:
    st.write("Please upload a CSV file and configure the filters.")

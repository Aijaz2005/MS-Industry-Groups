import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode,AgGridTheme
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, ColorBar, HoverTool, Spacer, Legend
from bokeh.transform import dodge
from bokeh.models import NumeralTickFormatter
from bokeh.models import Legend

# configuration of the page
st.set_page_config(layout="wide")

# Title
st.title("Industry Group Dashboard")

# Upload CSV file
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

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
    min_market_cap = st.sidebar.number_input("Minimum Market Cap", float(df['MarketCapital'].min()),
                                             float(df['MarketCapital'].max()), float(df['MarketCapital'].min()))
    filtered_df = df[df['MarketCapital'] >= min_market_cap]

    # Convert 'IndustryGroupRankCurrent', 'IndustryGroupRankLastWeek', and 'IndustryGroupRankLast3MonthsAgo' columns to numeric
    filtered_df['IndustryGroupRankCurrent'] = pd.to_numeric(filtered_df['IndustryGroupRankCurrent'], errors='coerce')
    filtered_df['IndustryGroupRankLastWeek'] = pd.to_numeric(filtered_df['IndustryGroupRankLastWeek'], errors='coerce')
    # filtered_df['IndustryGroupRankLast3MonthAgo'] = pd.to_numeric(filtered_df['IndustryGroupRankLast3MonthAgo'],errors='coerce')

    # Filter based on the condition
    filtered_df = filtered_df[(filtered_df['IndustryGroupRankCurrent'] < filtered_df['IndustryGroupRankLastWeek'])]

    # Calculate the difference between current rank and last week rank
    filtered_df['RankDifference'] = filtered_df['IndustryGroupRankCurrent'] - filtered_df['IndustryGroupRankLastWeek']

    # Create a grouped bar chart using Bokeh
    st.subheader("Comparison between Current Rank & Last Week Rank.")

    # Add a checkbox to turn on/off text labels
    show_labels = st.checkbox("Show Text Labels", value=True)

    # Calculate the length of industries
    industries = filtered_df['IndustryGroupName'].tolist()

    # Adjust the width based on the number of industries
    plot_width = max(len(industries) * 40, 800)  # Minimum width of 800 pixels

    source = ColumnDataSource(filtered_df)
    industries = source.data['IndustryGroupName'].tolist()
    current_rank = source.data['IndustryGroupRankCurrent'].tolist()
    weeks = source.data['IndustryGroupRankLastWeek'].tolist()

    p = figure(x_range=industries, height=400, title="Industry Group Rankings",
               toolbar_location="above", tools="pan,box_zoom,reset,save", y_range=(0, max(current_rank + weeks) + 5))

    p.vbar(x=dodge('IndustryGroupName', 0, range=p.x_range), top='IndustryGroupRankCurrent', width=0.2,
           source=source, fill_color="#3377FF", line_color="#3377FF", legend_label="Current Rank")

    p.vbar(x=dodge('IndustryGroupName', -0.2, range=p.x_range), top='IndustryGroupRankLastWeek', width=0.2,
           source=source, fill_color="#FF5733", line_color="#FF5733", legend_label="Last Week Rank")

    # Add text labels to the bars with smaller font size
    text_font_size = "8pt"

    # Add text labels to the bars
    if show_labels:
        p.text(x=dodge('IndustryGroupName', 0.0, range=p.x_range), y='IndustryGroupRankLast3MonthAgo',
               text='IndustryGroupRankLast3MonthAgo', text_align='center', text_baseline='bottom',
               source=source, y_offset=5, text_color="black", text_font_size=text_font_size)

        p.text(x=dodge('IndustryGroupName', -0.2, range=p.x_range), y='IndustryGroupRankLastWeek',
               text='IndustryGroupRankLastWeek', text_align='center', text_baseline='bottom',
               source=source, y_offset=-3, text_color="black", text_font_size=text_font_size)

        p.text(x=dodge('IndustryGroupName', 0, range=p.x_range), y='IndustryGroupRankCurrent',
               text='IndustryGroupRankCurrent', text_align='center', text_baseline='bottom',
               source=source, y_offset=1, text_color="black", text_font_size=text_font_size)

    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None

    # Add hover tooltips
    hover = HoverTool()
    hover.tooltips = [("Industry Group", "@IndustryGroupName"),
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

    # Show the chart
    st.bokeh_chart(p, use_container_width=True)

# Display filtered DataFrame with the desired column header
grid_options = {
    "domLayout": "autoHeight",
    "animateRows": False,
    "enableColResize": False,
    "enableFilter": True,
    "suppressCellSelection": True,
    "suppressAutoSize": False,
    "suppressMultiSort": False,
    "suppressMovableColumns": False,
    "suppressMakeColumnVisibleAfterUnGroup": False,
    "enableRangeSelection": True,
    "pivotTotals": False,
    "theme": "ag-theme-material",
    "columnDefs": [
        {
            "headerName": "Industry Group",
            "field": "IndustryGroupName",
            "sortable": True,  # Enable sorting for this column
            "filter": "agTextColumnFilter"
        },
        {
            "headerName": "Number of Stocks",
            "field": "NumberOfStocks",
            "sortable": True,  # Enable sorting for this column
            "filter": "agTextColumnFilter"
        },
        {
            "headerName": "Rank Difference",
            "field": "RankDifference",
            "sortable": True  # Enable sorting for this column
            "filter": "agTextColumnFilter"
        },
        {
            "headerName": "Current Rank",  # Change the column header here
            "field": "IndustryGroupRankCurrent",
            "sortable": True  # Enable sorting for this column
        },
        {
            "headerName": "Last Week Rank",
            "field": "IndustryGroupRankLastWeek",
            "sortable": True  # Enable sorting for this column
        },
        {
            "headerName": "Last 3month Rank",
            "field": "IndustryGroupRankLast3MonthAgo",
            "sortable": True  # Enable sorting for this column
        },
        {
            "headerName": "Market Capital",
            "field": "MarketCapital",
            "sortable": True  # Enable sorting for this column
        }
    ]
}
if 'filtered_df' in locals():
    st.subheader("Filtered Data")
    AgGrid(data=filtered_df, gridOptions=grid_options,columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
#grid = AgGrid(
#    data=filtered_df,
#    gridOptions=grid_options,  # Apply sorting to columns
#    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
#)


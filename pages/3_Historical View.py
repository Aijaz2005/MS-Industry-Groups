import pandas as pd
import os
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode

# Configuration of the page
st.set_page_config(layout="wide")

# Step 1: Create a Streamlit app
st.title("Historical View of Industry Groups")

# Create a grouped bar chart using Bokeh
st.subheader("Here you can upload multiple CSV files.")

# Step 2: File uploader
uploaded_files = st.file_uploader("Upload CSV files", accept_multiple_files=True, type=["csv"])


# Define a function to process CSV files
@st.cache_data
def process_csv_files(files):
    all_data = []
    for file in files:
        data = pd.read_csv(file, index_col=False, skiprows=0)

        # Dropping columns
        data = data.drop(columns=['Sno', 'Symbol', 'IndustryGroupRankLast6MonthAgo', 'PricePercentChangeYTD'])

        # Convert 'MarketCapital' column to string if not already
        if not pd.api.types.is_string_dtype(data['MarketCapital']):
            data['MarketCapital'] = data['MarketCapital'].astype(str)

        # Remove unwanted characters from 'MarketCapital' column
        data['MarketCapital'] = data['MarketCapital'].str.replace(',', '').str.replace(' Cr', '')

        # Convert 'MarketCapital' column to float
        data['MarketCapital'] = pd.to_numeric(data['MarketCapital'], errors='coerce')

        # Extract the file name without extension and use it as the 'Date' column
        file_name = os.path.splitext(os.path.basename(file.name))[0]
        data['Date'] = pd.to_datetime(file_name, format='%d-%m-%Y')  # Extract date as datetime object

        all_data.append(data)

    # Concatenate the data from uploaded files
    if all_data:
        industry_data = pd.concat(all_data, ignore_index=True)
        return industry_data
    else:
        return None


# Call the function to process CSV files
industry_data = process_csv_files(uploaded_files)

# Sidebar for filter options
st.sidebar.header("Filter Options")

# Step 3: Filter data based on market cap
if industry_data is not None:
    # Allow user to choose the market cap range
    min_market_cap = st.sidebar.number_input("Minimum Market Cap", float(industry_data['MarketCapital'].min()),
                                             float(industry_data['MarketCapital'].max()),
                                             float(industry_data['MarketCapital'].min()))
    max_market_cap = st.sidebar.number_input("Maximum Market Cap", float(min_market_cap),
                                             float(industry_data['MarketCapital'].max()),
                                             float(industry_data['MarketCapital'].max()))

    industry_data = industry_data[(industry_data['MarketCapital'] >= min_market_cap) &
                                  (industry_data['MarketCapital'] <= max_market_cap)]

# Step 4: Radio button for choosing display option
display_option = st.sidebar.radio("Display Option", ["Use Multiselect", "Show All Data"], index=0)

# Warning message for "Show All Data" option
if display_option == "Show All Data":
    st.sidebar.warning("Warning: Loading all data may take time and can slow down the app.")

# Filter data based on the display option
if industry_data is not None:
    if display_option == "Use Multiselect":
        selected_groups = st.multiselect("Select Industry Groups", industry_data['IndustryGroupName'].unique())
        filtered_data = industry_data[industry_data['IndustryGroupName'].isin(selected_groups)]
    else:
        filtered_data = industry_data
else:
    filtered_data = None

# Calculate the 'RankDecrease' column
if filtered_data is not None:
    filtered_data['IndustryGroupRankCurrent'] = pd.to_numeric(filtered_data['IndustryGroupRankCurrent'],
                                                              errors='coerce')
    filtered_data['IndustryGroupRankLastWeek'] = pd.to_numeric(filtered_data['IndustryGroupRankLastWeek'],
                                                               errors='coerce')

    # Calculate RankDecrease
    filtered_data['RankDecrease'] = filtered_data['IndustryGroupRankCurrent'] - filtered_data[
        'IndustryGroupRankLastWeek']

    # Sort the DataFrame by the "Date" column in descending order
    filtered_data = filtered_data.sort_values(by="Date", ascending=False)

    # Display the combined data including RankDecrease column
    grid = AgGrid(
        data=filtered_data,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW
    )
else:
    st.write("No CSV files uploaded.")

import streamlit as st
import pandas as pd
import urllib.parse

# App title
st.title("Keyword Landscape & Share of Voice Tracker")

# File upload
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file:
    # Read CSV into DataFrame
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')

    # Renaming columns for clarity, adjust these if column names are different
    df.columns = ['Keyword', 'URL', 'Blended Rank', 'Search Volume', 'CPC']

    # Sorting based on Blended Rank (ascending) and Search Volume (descending)
    df = df.sort_values(by=['URL', 'Blended Rank', 'Search Volume'], ascending=[True, True, False])

    # User input for number of keywords to select per URL
    keyword_limit = st.slider("Select the number of top keywords per URL:", 1, 25, 5)

    # Function to extract subfolder levels from URLs
    def extract_subfolders(url):
        parsed_url = urllib.parse.urlparse(url)
        subfolders = parsed_url.path.strip('/').split('/')
        subfolder_dict = {f"L{i}": subfolder.capitalize() for i, subfolder in enumerate(subfolders)}
        return subfolder_dict

    # Create a new DataFrame for results
    result = pd.DataFrame(columns=[
        'URL', 'Keyword', 'Blended Rank', 'Search Volume', 'CPC', 
        # Placeholder for subfolder columns
    ])

    rows_to_append = []  # Temporary list to hold data before converting to DataFrame

    # Group data by URL and process each group
    for url, group in df.groupby('URL'):
        # Select top keywords per the user-selected limit
        top_keywords = group.head(keyword_limit)

        for _, row in top_keywords.iterrows():
            # Create a dictionary for the row data
            new_row = {
                'URL': url,
                'Keyword': row['Keyword'],
                'Blended Rank': row['Blended Rank'],
                'Search Volume': row['Search Volume'],
                'CPC': row.get('CPC', 'N/A')  # Handle missing CPC values
            }
            # Add subfolder data to the row
            subfolders = extract_subfolders(url)
            new_row.update(subfolders)
            rows_to_append.append(new_row)

    # Convert list of dicts to DataFrame
    result = pd.DataFrame(rows_to_append)

    # Display the result in Streamlit
    st.write("Filtered Keywords:", result)

    # Provide download button for the result
    st.download_button(
        label="Download as Excel",
        data=result.to_excel(index=False, engine='openpyxl'),
        file_name='keyword_landscape.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

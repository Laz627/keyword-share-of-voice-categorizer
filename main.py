import streamlit as st
import pandas as pd
import urllib.parse

# App title and creator information
st.title("Keyword Landscape & Share of Voice Tracker")
st.markdown("""
### Developed by Brandon Lazovic

This tool helps you quickly develop a comprehensive keyword landscape and share of voice tracking set without manually reviewing thousands of keywords. It allows you to:

- Upload your CSV file containing keywords, URLs, blended ranks, search volumes, and optional CPC data.
- Prioritize top keywords based on rank (lower is better) and search volume (higher is better).
- Extract and categorize subfolder levels from URLs to understand keyword distribution across different site sections.
- Download the processed data in Excel format for further analysis.

**Instructions:**
1. Upload your CSV file using the uploader below.
2. Choose the number of top keywords per URL to include in the analysis.
3. View the results and download the processed data.
4. Include the following header names in your CSV: 'Keyword', 'URL', 'Blended Rank', 'Search Volume', 'CPC'.

""")

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

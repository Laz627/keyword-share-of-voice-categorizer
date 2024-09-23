import streamlit as st
import pandas as pd
import urllib.parse
from io import BytesIO

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
2. Choose the number of top keywords per URL to include in the analysis using the slider.
3. Optionally, include additional top keywords based on overall search volume.
4. Click the "Generate Results" button to view the results and download the processed data.

""")

# File upload
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file:
    # Read CSV into DataFrame
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')

    # Renaming columns if needed to match expected format
    df.columns = ['URL', 'Keyword', 'Blended Rank', 'Search Volume', 'CPC']

    # Clean and drop any rows with missing or malformed data
    df = df.dropna(subset=['Keyword', 'URL', 'Blended Rank', 'Search Volume'])

    # Sorting based on Blended Rank (ascending) and Search Volume (descending)
    df = df.sort_values(by=['URL', 'Blended Rank', 'Search Volume'], ascending=[True, True, False])

    # User input for number of keywords to select per URL
    keyword_limit = st.slider("Select the number of top keywords per URL:", 1, 25, 5)

    # Option to include additional keywords based on top overall search volume
    include_top_search_volume = st.checkbox("Include top keywords based on overall search volume")

    # Button to generate results
    if st.button("Generate Results"):
        # Function to extract subfolder levels from URLs
        def extract_subfolders(url):
            try:
                parsed_url = urllib.parse.urlparse(url)
                domain = parsed_url.netloc.replace('www.', '').split('.')[0].capitalize()
                subfolders = [segment for segment in parsed_url.path.strip('/').split('/') if segment]
                subfolder_dict = {f"L{i+1}": subfolder.replace('-', ' ').capitalize() for i, subfolder in enumerate(subfolders)}
                subfolder_dict['L0'] = domain
                return subfolder_dict
            except Exception as e:
                return {}

        # Create a new DataFrame for results
        result = pd.DataFrame(columns=[
            'URL', 'Keyword', 'Blended Rank', 'Search Volume', 'CPC'
        ])

        rows_to_append = []  # Temporary list to hold data before converting to DataFrame

        # Group data by URL and process each group
        for url, group in df.groupby('URL'):
            # Select top keywords per the user-selected limit
            top_keywords = group.head(keyword_limit)

            for _, row in top_keywords.iterrows():
                # Ensure the URL is correctly parsed and not malformed
                if not isinstance(url, str):
                    continue

                # Create a dictionary for the row data
                new_row = {
                    'URL': url,
                    'Keyword': row['Keyword'],
                    'Blended Rank': row['Blended Rank'],
                    'Search Volume': row['Search Volume'],
                    'CPC': row.get('CPC', 'N/A')  # Handle missing CPC values
                }
                # Add subfolder data to the row based on URL
                subfolders = extract_subfolders(url)
                new_row.update(subfolders)
                rows_to_append.append(new_row)

        # If the user chose to include additional top search volume keywords
        if include_top_search_volume:
            # Select the top keywords based on search volume across the entire DataFrame
            top_volume_keywords = df.sort_values(by='Search Volume', ascending=False).head(keyword_limit)
            for _, row in top_volume_keywords.iterrows():
                new_row = {
                    'URL': row['URL'],
                    'Keyword': row['Keyword'],
                    'Blended Rank': row['Blended Rank'],
                    'Search Volume': row['Search Volume'],
                    'CPC': row.get('CPC', 'N/A')
                }
                subfolders = extract_subfolders(row['URL'])
                new_row.update(subfolders)
                rows_to_append.append(new_row)

        # Convert list of dicts to DataFrame
        result = pd.DataFrame(rows_to_append)

        # Remove duplicates if keywords appear in both URL-specific and top volume selections
        result = result.drop_duplicates(subset=['URL', 'Keyword'])

        # Display the result in Streamlit
        st.write("Filtered Keywords:", result)

        # Convert DataFrame to Excel format in-memory
        output = BytesIO()
        result.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        # Provide download button for the result
        st.download_button(
            label="Download as Excel",
            data=output,
            file_name='keyword_landscape.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

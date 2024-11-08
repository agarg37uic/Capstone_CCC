import streamlit as st
import pandas as pd
import re
from TRY8Q6 import scrape_pw_trader  # Make sure TRY8Q6.py is in the same directory

# General-purpose function to parse natural language queries
def parse_query(query):
    record_limit = None  # Initialize with None to identify missing values later
    sort_order = None
    keyword = None

    # Dynamic limit extraction (e.g., "top 6" or "6 records")
    limit_match = re.search(r"top (\d+)|(\d+) records", query)
    if limit_match:
        record_limit = int(limit_match.group(1) or limit_match.group(2))

    # Keyword extraction based on common request patterns
    keyword_match = re.search(r"prices? of ([\w\s]+)|get ([\w\s]+)", query)
    if keyword_match:
        keyword = keyword_match.group(1) or keyword_match.group(2)
    else:
        # Fallback to infer main keyword from remaining text
        keyword = re.sub(r"get|top \d+|low to high|high to low", "", query).strip()

    # Sorting extraction (low to high or high to low)
    if "low to high" in query:
        sort_order = "ascend"
    elif "high to low" in query:
        sort_order = "descend"

    return keyword, record_limit, sort_order

# Streamlit UI setup
st.title("PWC Trader Flexible Natural Language Scraper")
st.write("Enter a flexible natural language query to search listings on PWC Trader.")

# Query input field
query = st.text_input("Enter your query", value="get top 6 items low to high price")

# Button to trigger the scraping
if st.button("Search"):
    st.write("Interpreting query...")

    # Parse the query
    keyword, record_limit, sort_order = parse_query(query)
    st.write(f"Searching for: '{keyword or 'all items'}' with limit: {record_limit or 'default'} and sorting: {sort_order or 'no sorting'}.")

    # Execute the scraping function with parsed inputs
    try:
        # Use parsed keyword and record limit in scraping
        data = scrape_pw_trader(query=keyword, record_limit=record_limit if record_limit else 20)

        # Apply sorting if requested and data contains a 'price' column
        if not data.empty and sort_order and 'price' in data.columns:
            data = data.sort_values(by="price", ascending=(sort_order == "ascend"))
            
        # Display results
        if not data.empty:
            st.write("Search Results:")
            st.dataframe(data)
        else:
            st.write("No data found.")
    except Exception as e:
        st.write("An error occurred during scraping:", e)

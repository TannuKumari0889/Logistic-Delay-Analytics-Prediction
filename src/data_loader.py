# src/data_loader.py
import os
import gdown
import pandas as pd
import streamlit as st
from src.config import TABLE_LINKS

def extract_file_id(link):
    """
    Extracts the file ID from a Google Drive link.
    Works with /d/<id>/view and ?id=<id> links.
    """
    if "/d/" in link:
        return link.split("/d/")[1].split("/")[0]
    elif "id=" in link:
        return link.split("id=")[1].split("&")[0]
    else:
        raise ValueError(f"Cannot extract file ID from link: {link}")


@st.cache_data
def load_table(table_name):
    """
    Downloads a table from Google Drive if not cached and loads it as a pandas DataFrame.
    """
    link = TABLE_LINKS[table_name]
    file_id = extract_file_id(link)

    os.makedirs("data", exist_ok=True)
    output_path = f"data/{table_name}.csv"

    if not os.path.exists(output_path):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, output_path, quiet=False)

    df = pd.read_csv(output_path)

    # Convert dates automatically if possible
    for col in df.columns:
        if "date" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
            except:
                pass

    return df


@st.cache_data
def load_all_tables():
    """
    Loads all tables from TABLE_LINKS and returns a dictionary.
    """
    data_dict = {}
    for name in TABLE_LINKS:
        try:
            data_dict[name] = load_table(name)
        except Exception as e:
            st.warning(f"Failed to load table {name}: {e}")
            data_dict[name] = pd.DataFrame()  # empty dataframe if fail
    return data_dict

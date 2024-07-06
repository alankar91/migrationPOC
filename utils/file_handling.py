import pandas as pd
import numpy as np
import streamlit as st

def split_dataframe(df, chunk_size):
    return [df.iloc[i:i + chunk_size] for i in range(0, len(df), chunk_size)]

def df_to_markdown(df):
    df = df.replace(np.nan, '', regex=True)
    header = "| " + " | ".join(df.columns) + " |"
    separator = "|---" * len(df.columns) + "|"
    rows = []
    for _, row in df.iterrows():
        formatted_row = "| " + " | ".join(str(x) if x != 'nan' else '-' for x in row) + " |"
        rows.append(formatted_row)
    return "\n".join([header, separator] + rows)

def read_source1_file(st):
    source_file_uploaded = st.sidebar.file_uploader(
        "Step 1: Upload your first TPA Excel/CSV data file.", 
        type=['csv','xlsx'],
        accept_multiple_files=False,
        key="source1FileUploader"
    )
    if source_file_uploaded is not None:
        source_table_df = pd.read_excel(source_file_uploaded)
        file_name = source_file_uploaded.name

        num_rows, num_columns = source_table_df.shape
        

        return df_to_markdown(source_table_df), [file_name, num_rows, num_columns], source_table_df
    else:
        return "", [], pd.DataFrame()

def read_source2_file(st):
    source_file_uploaded = st.sidebar.file_uploader(
        "Step 2: Upload your second TPA Excel/CSV data file.", 
        type=['csv','xlsx'],
        accept_multiple_files=False,
        key="source2FileUploader"
    )
    if source_file_uploaded is not None:
        source_table_df = pd.read_excel(source_file_uploaded)
        file_name = source_file_uploaded.name

        num_rows, num_columns = source_table_df.shape
        

        return df_to_markdown(source_table_df), [file_name, num_rows, num_columns], source_table_df
    else:
        return "", [], pd.DataFrame()

def read_target_file(st, target_table_chunk_size):
    target_file_uploaded = st.sidebar.file_uploader(
        "Step 3: Upload your target Excel/CSV file.", 
        type=['csv','xlsx'],
        accept_multiple_files=False,
        key="targetFileUploader"
    )
    if target_file_uploaded is not None:
        target_table_df = pd.read_excel(target_file_uploaded)
        file_name = target_file_uploaded.name
        
        # Get the number of rows and columns
        num_rows, num_columns = target_table_df.shape

        # Extracting the necessary columns and adding new columns for mappings
        target_table_clean_df = target_table_df[['Target Column Name', 'Target Column DataType']].copy()
        target_table_clean_df['Source1 Column Name'] = np.nan
        target_table_clean_df['Source1 Mapping'] = np.nan
        target_table_clean_df['Source2 Column Name'] = np.nan
        target_table_clean_df['Source2 Mapping'] = np.nan
        target_table_chunks = split_dataframe(target_table_clean_df, target_table_chunk_size)
        
        return [df_to_markdown(chunk) for chunk in target_table_chunks], file_name, [file_name, num_rows, num_columns], target_table_clean_df
    else:
        return [], "", [], pd.DataFrame()
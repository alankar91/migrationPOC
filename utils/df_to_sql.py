import sqlite3
import pandas as pd

def clean_string(text):
    """
    Clean the input string by replacing characters that may cause problems in SQL queries.

    Args:
        text (str): The input string to be cleaned.

    Returns:
        str: The cleaned string.
    """
    # Replace problematic characters with underscores
    cleaned_text = text.replace("\\", "\\\\").replace("'", "\\'")
    return cleaned_text

def df_to_sql(df, table_name, drop_existing_table=False):
    """
    Convert a pandas DataFrame to SQL commands for creating a table and inserting data,
    then execute these commands to test them.

    Args:
        df (pandas.DataFrame): The DataFrame to be converted to SQL.
        table_name (str): The name of the table to be created.
        drop_existing_table (bool, optional): If True, drop the existing table before creating a new one.

    Returns:
        str: SQL commands as a string.

    Raises:
        ValueError: If the DataFrame is empty or has no columns.
    """
    if df.empty or len(df.columns) == 0:
        raise ValueError("The DataFrame is empty or has no columns.")

    # SQL commands for database and table creation
    sql_commands = []

    # Drop existing table if specified
    if drop_existing_table:
        sql_commands.append("-- Drop the table if it already exists to avoid duplication errors")
        sql_commands.append(f"DROP TABLE IF EXISTS {table_name};\n")

    # Start with the CREATE TABLE command
    create_table = "-- Create a new table\n"
    create_table += f"CREATE TABLE {table_name} (\n"
    columns = []
    for col, dtype in zip(df.columns, df.dtypes):
        # Clean column names to avoid problematic characters
        if dtype == 'int64':
            sql_type = 'INTEGER'
        elif dtype == 'float64':
            sql_type = 'REAL'
        elif dtype == 'bool':
            sql_type = 'BOOLEAN'
        else:
            sql_type = 'TEXT'
        columns.append(f'    "{col}" {sql_type} NOT NULL')
    create_table += ',\n'.join(columns) + "\n);\n"
    sql_commands.append(create_table)

    # Add a comment before the INSERT INTO command
    sql_commands.append("-- Insert records into the table")

    # Now the INSERT INTO commands
    column_names = ', '.join(f'\"{col}\"' for col in df.columns)
    insert_into = f"INSERT INTO {table_name} ({column_names}) VALUES\n"
    values_list = []
    for _, row in df.iterrows():
        values = ', '.join([f"'{clean_string(x)}'" if isinstance(x, str) else clean_string(str(x)) for x in row])
        values_list.append(f"    ({values})")
    insert_into += ',\n'.join(values_list) + ";\n"
    sql_commands.append(insert_into)

    # Add a comment before the SELECT command
    sql_commands.append("-- Select all records from the table to verify insertion")
    sql_commands.append(f"SELECT * FROM {table_name};")

    # Combine all SQL commands into one script
    full_sql_script = '\n'.join(sql_commands)

    # Return the SQL commands as a string
    return full_sql_script

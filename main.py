import streamlit as st
import pandas as pd

from utils.file_handling import (
    read_source1_file,
    read_source2_file,
    read_target_file,
)
from utils.processing import (
    get_qa_chain,
    process_target_table,
    create_excel_file,
)
from utils.constants import (
    target_table_chunk_size,
    model_max_tokens,
    excel_title_height,
    excel_header_height,
    excel_data_height,
    max_header_weight,
    min_header_weight,
)

from utils.openai_api import get_openai_api_key, display_api_key

from utils.df_to_sql import df_to_sql

st.set_page_config(
    page_title="Migration AI", 
    initial_sidebar_state="auto"
)

def initialize_session_state():
    if 'output_display_title' not in st.session_state:
        st.session_state.output_display_title = st.empty()
    if 'output_display_subtitle' not in st.session_state:
        st.session_state.output_display_subtitle = st.empty()
    if 'output_display' not in st.session_state:
        st.session_state.output_display = st.empty()
    if 'show_download' not in st.session_state:
        st.session_state.show_download = False
    if 'excel_data' not in st.session_state:
        st.session_state.excel_data = ""
    if 'download_filename' not in st.session_state:
        st.session_state.download_filename = ""
    if 'combined_df' not in st.session_state:
        st.session_state.combined_df = pd.DataFrame()
    if 'OPENAI_API_KEY_Session' not in st.session_state:
        st.session_state.OPENAI_API_KEY_Session = ""
    
def handle_file_uploads():
    source1_table_markdown, source1_table_data, source1_table_df = read_source1_file(st)
    source2_table_markdown, source2_table_data, source2_table_df = read_source2_file(st)

    source1_file_col, source2_file_col, target_file_col = st.columns([1,1,1])

    with source1_file_col:
        if len(source1_table_data) > 0 and source1_table_data[0] and source1_table_data[1] and source1_table_data[2]:
            st.text_input(label="Source1 File", value=source1_table_data[0], disabled=True)
            info_message = (f"""({source1_table_data[1]} row x {source1_table_data[2]} column)""")
            st.caption(info_message)
        else:
            st.info('Please Upload Source1 File', icon="ℹ️")

    with source2_file_col:
        if len(source2_table_data) > 0 and source2_table_data[0] and source2_table_data[1] and source2_table_data[2]:
            st.text_input(label="Source2 File", value=source2_table_data[0], disabled=True)
            info_message = (f"""({source2_table_data[1]} row x {source2_table_data[2]} column)""")
            st.caption(info_message)
        else:
            st.info('Please Upload Source2 File', icon="ℹ️")

    target_table_markdowns, target_filename, target_table_data, target_table_clean_df = read_target_file(st, target_table_chunk_size)

    with target_file_col:
        if len(target_table_data) > 0 and target_table_data[0] and target_table_data[1] and target_table_data[2]:
            st.text_input(label="Target File", value=target_table_data[0], disabled=True)
            info_message = (f"""({target_table_data[1]} row x {target_table_data[2]} column)""")
            st.caption(info_message)
        else:
            st.info('Please Upload a Target File', icon="ℹ️")

    return source1_table_markdown, source2_table_markdown, target_table_markdowns, target_filename, [source1_table_df, source2_table_df, target_table_clean_df]

def get_response(source1_table_markdown, source2_table_markdown, target_table_markdowns, target_filename, ai_model_name, model_max_tokens, openai_api_key):
    error_msg = st.empty()
    if (not source1_table_markdown) or (source1_table_markdown == "") \
        or (not source2_table_markdown) or (source2_table_markdown == "") \
        or (not target_table_markdowns) or (len(target_table_markdowns) == 0):
        error_msg.write("Please upload all 3 necessary files to continue...")
        return

    llm_chain = get_qa_chain(openai_api_key, ai_model_name, model_max_tokens)

    try:
        combined_df, progress_bar = process_target_table(
          source1_table_markdown, source2_table_markdown, target_table_markdowns, 
          llm_chain, target_table_chunk_size
        )

        progress_bar.empty()
        st.balloons()
        
        st.session_state["combined_df"] = combined_df
        st.rerun()
    except Exception as e:
        st.error('Sorry, there was an error, please try again', icon="🚨")
        st.session_state["combined_df"] = pd.DataFrame()
    
def main():
    genre_name = ["Mapping Generator", "Mapping SQL Code Generator"]
    with st.sidebar:
        genre = st.sidebar.radio(
            "Select Use Case",
            genre_name,
            index=0,
        )
    st.markdown('<h2 style="text-align:center">Migration Generation AI</h2>', unsafe_allow_html=True)
    st.divider()

    st.subheader(genre + ":")

    initialize_session_state()

    source1_table_markdown, source2_table_markdown, target_table_markdowns, target_filename, dfs = handle_file_uploads()
    
    st.divider()

    process_btn_col, _, download_btn_col = st.columns([1,1,1])

    if not st.session_state["combined_df"].empty:
        create_excel_file(
          st.session_state["combined_df"], st.session_state, excel_title_height, excel_header_height, 
          excel_data_height, max_header_weight, min_header_weight, target_filename
        )

        full_sql_script = df_to_sql(
            st.session_state["combined_df"], 
            "migration_ai_mapped_data", 
            drop_existing_table=True
        )

        if genre == genre_name[1]:
            st.caption("SQL Script of the Mapped Data:")
            st.text_area(
                "SQL Script of the Mapped Data:", 
                full_sql_script, 
                label_visibility="collapsed",
                height=150
            )

        st.caption("Your Mapped Data:")
        st.dataframe(st.session_state["combined_df"])

        if st.session_state.show_download:
            with download_btn_col:
                if genre == genre_name[0]:
                    download_btn = st.download_button(
                        label="Download the Data (in Excel)",
                        data=st.session_state.excel_data,
                        file_name=st.session_state.download_filename,
                        mime="application/vnd.ms-excel",
                    )
                elif genre == genre_name[1]:
                    st.download_button(
                        label="Download the Data (in SQL)",
                        data=full_sql_script,
                        file_name='migration_ai_mapped_data_db.sql',
                        mime='text/plain'
                    )

    with st.sidebar:
        model_name = st.sidebar.radio(
            "Select GPT Model",
            ["3.5", "4o"],
            index=0,
            horizontal=True,
        )

        st.divider()
        get_openai_api_key()
        display_api_key()

        OPENAI_API_KEY_Session = st.session_state.get('OPENAI_API_KEY_Session', "<your OpenAI API key if not set as an env var>")

    ai_model_name_input = ""

    if model_name and model_name == "3.5":
        ai_model_name_input = "gpt-3.5-turbo"
    elif model_name and model_name == "4o":
        ai_model_name_input = "gpt-4o"

    if ai_model_name_input:
        with process_btn_col:
            submitted = st.button(
                    "Start Processing Data", 
                    type="primary",
                    disabled = not OPENAI_API_KEY_Session or not source1_table_markdown or not source2_table_markdown or not target_table_markdowns
                    )
            if submitted:
                get_response(
                    source1_table_markdown, 
                    source2_table_markdown, 
                    target_table_markdowns, 
                    target_filename, 
                    ai_model_name_input,
                    model_max_tokens,
                    OPENAI_API_KEY_Session
                )

    if not dfs[0].empty or not dfs[1].empty or not dfs[2].empty:
        st.divider()

        if not dfs[0].empty:
            st.caption("1. Source1 Table Data:")
            st.dataframe(dfs[0])

        if not dfs[1].empty:
            st.caption("2. Source2 Table Data:")
            st.dataframe(dfs[1])
        
        if not dfs[2].empty:
            st.caption("3. Target Table Data:")
            st.dataframe(dfs[2])

if __name__ == "__main__":
    main()

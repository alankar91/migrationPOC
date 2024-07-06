import streamlit as st

def get_openai_api_key():
    try:
        if "OPENAI_API_KEY" in st.secrets:
            st.session_state.OPENAI_API_KEY_Session = st.secrets["OPENAI_API_KEY"]
    except Exception as e:
        print(e)
    if not st.session_state["OPENAI_API_KEY_Session"] or st.session_state["OPENAI_API_KEY_Session"] == "None":
        openai_api_key_input = st.text_input(
            "Please Enter your OpenAI API key:", 
            type="password"
        )
        if openai_api_key_input:
            st.session_state["OPENAI_API_KEY_Session"] = openai_api_key_input
        else:
            st.session_state["OPENAI_API_KEY_Session"] = ""

# Function to mask the OpenAI API key
def mask_api_key(api_key):
    if len(api_key) > 8:
        return f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}"
    else:
        return api_key  # Return the key as is if it's too short to mask

def display_api_key():
    if st.session_state["OPENAI_API_KEY_Session"] != "":
        st.write(f"Using OpenAI API key: \n\
            {mask_api_key(st.session_state['OPENAI_API_KEY_Session'])}")
        st.markdown("<br/><br/>", unsafe_allow_html=True)
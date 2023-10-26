import streamlit as st
from helper_functions import read_file_contents, add_logo

st.set_page_config(
    page_title="Introduction",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded",
)

add_logo()

st.title("Welcome to the Discrete Event Simulation Playground! 👋")

st.markdown(read_file_contents('resources/introduction_text.md'))

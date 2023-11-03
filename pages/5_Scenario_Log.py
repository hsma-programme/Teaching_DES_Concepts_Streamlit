import streamlit as st
import pandas as pd

from helper_functions import read_file_contents, add_logo, mermaid
from model_classes import *
# from st_pages import show_pages_from_config, add_page_title
import plotly.express as px


st.set_page_config(
     page_title="The Full Model",
     layout="wide",
     initial_sidebar_state="expanded",
 )

# Initialise session state
if 'session_results' not in st.session_state:
    st.session_state['session_results'] = []

# add_page_title()

# show_pages_from_config()

add_logo()

with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)
    

## We add in a title for our web app's page
st.title("Discrete Event Simulation Playground")
st.subheader("How can we optimise the full system?")

if len(st.session_state['session_results']) > 0:

    all_run_results = pd.concat(st.session_state['session_results'])

    st.write(all_run_results.median().T)
else:
    st.markdown("No scenarios yet run. Go to 'The Full Model' page.")
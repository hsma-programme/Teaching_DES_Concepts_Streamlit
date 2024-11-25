'''
A Streamlit application based on Monks and 

Allows users to interact with an increasingly more complex treatment simulation 
'''
import streamlit as st

from helper_functions import read_file_contents, add_logo, mermaid
from model_classes import *
# from st_pages import show_pages_from_config, add_page_title

st.set_page_config(
     page_title="Adding another Resource Type",
     layout="wide",
     initial_sidebar_state="expanded",
 )

# add_page_title()

# show_pages_from_config()

add_logo()

with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

## We add in a title for our web app's page
st.title("Discrete Event Simulation Playground")
st.subheader("Who is treating these people, and where?")

tab1, tab2, tab3 = st.tabs(["Introduction", "Exercise", "Playground"])

with tab1:
    st.markdown(read_file_contents('resources/room_resource_text.md'))

    mermaid(height=425, code=
    """
    %%{ init: { 'flowchart': { 'curve': 'step' } } }%%
    %%{ init: {  'theme': 'base', 'themeVariables': {'lineColor': '#b4b4b4'} } }%%
    flowchart LR
    A[Arrival]----> B[Treatment]
    B <-.-> C([Nurse\n<b>RESOURCE</b>])
    B <-.-> D([Cubicle\n<b>RESOURCE</b>])
    C -.-> B
    D -.-> B

    B ----> F{{Discharge to community\n<b>No delay</b>}}
    B ----> G{{Discharge to ward\n<b>May be a delay</b>}}

    classDef default font-size:18pt,font-family:lexend;
    linkStyle default stroke:white;
    """
    )

with tab2:
    st.markdown(read_file_contents('resources/room_resource_exercise.md'))

'''
A Streamlit application based on Monks and 

Allows users to interact with an increasingly more complex treatment simulation 
'''
import streamlit as st

from helper_functions import read_file_contents, add_logo, mermaid
from model_classes import *
# from st_pages import show_pages_from_config, add_page_title

st.set_page_config(
     page_title="Adding an Optional Step",
     layout="wide",
     initial_sidebar_state="expanded",
 )

# show_pages_from_config()

add_logo()

with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

## We add in a title for our web app's page
st.title("Discrete Event Simulation Playground")
st.subheader("Making Patients Behave Differently: Adding in an Optional Step")

mermaid(height=225, code=
    """
            %%{ init: { 'flowchart': { 'curve': 'step' } } }%%
            %%{ init: {  'theme': 'base', 'themeVariables': {'lineColor': '#b4b4b4'} } }%%
            flowchart LR
            
            A[Arrival]----> B[Advice]
            
            B -.-> F([Nurse/Cubicle])
            F -.-> B
            
            B----> C[Treatment]

            C -.-> G([Nurse/Cubicle])
            G -.-> C

            B ----> Z[Discharge]
            C ----> Z

            classDef default font-size:18pt,font-family:lexend;
            linkStyle default stroke:white;
        """
    )


st.markdown(read_file_contents('resources/entity_paths_text.md'))

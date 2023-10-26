'''
A Streamlit application based on Monks and 

Allows users to interact with an increasingly more complex treatment simulation 
'''
import streamlit as st

from helper_functions import read_file_contents, add_logo
from model_classes import *


st.set_page_config(
     page_title="Adding another Resource Type",
     layout="wide",
     initial_sidebar_state="expanded",
 )

add_logo()

## We add in a title for our web app's page
st.title("Discrete Event Simulation Playground")
st.subheader("Where are they treating these people?")

st.markdown(read_file_contents('resources/room_resource_text.md'))

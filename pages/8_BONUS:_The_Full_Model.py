import streamlit as st


from helper_functions import read_file_contents, add_logo, mermaid
from model_classes import *
# from st_pages import show_pages_from_config, add_page_title

st.set_page_config(
     page_title="Find Out More",
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

st.subheader("Bonus: The complete model")

st.markdown(
    """
    We didn't have time today to explore the effects of having two types of resource on our final model. 

    We also locked off some of the parameters that can be adjusted in the model. 

    Here, we've added in nurses as a separate resource to  you can play around with every possible parameter too, like the average time it takes to triage a patient.
    """
)
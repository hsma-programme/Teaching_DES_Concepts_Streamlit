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

tab1, tab2, tab3 = st.tabs(["Introduction", "Exercise", "Playground"])

with tab1:

    st.markdown("""
                Now, it's not as simple as all of our patients being looked at by a nurse and then sent on their merry way.

                Some of them - but not all of them - may require another step where they undergo some treatment.
                
                So for some people, their pathway looks like this:
                """)


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

                C ----> Z[Discharge]

                classDef default font-size:18pt,font-family:lexend;
                linkStyle default stroke:white;
            """
        )

    st.markdown("But for other simpler cases, their pathway still looks like this!")

    mermaid(height=225, code=
        """
                %%{ init: { 'flowchart': { 'curve': 'step' } } }%%
                %%{ init: {  'theme': 'base', 'themeVariables': {'lineColor': '#b4b4b4'} } }%%
                flowchart LR
                
                A[Arrival]----> B[Advice]
                
                B -.-> F([Nurse/Cubicle])
                F -.-> B
                
                B ----> Z[Discharge]

                classDef default font-size:18pt,font-family:lexend;
                linkStyle default stroke:white;
            """
        )

    st.markdown(
        """
        So how do we ensure that some of our patients go down one pathway and not the other?

        You guessed it - the answer is sampling from a distribution again! 

        We can tell the computer the rough split we'd like to say - let's say 30% of our patients need the treatment step, but the other 70% will 

        And as before, there will be a bit of randomness, just like in the real world.
        In one simulation, we might end up with a 69/31 split, and the next might be 72/28, but it will always be around the expected split we've asked for.
        """
    )

    st.markdown(
        """
        We can think of our pathway as looking like this overall:
        """
    )

    mermaid(height=225, code=
        """
                %%{ init: { 'flowchart': { 'curve': 'step' } } }%%
                %%{ init: {  'theme': 'base', 'themeVariables': {'lineColor': '#b4b4b4'} } }%%
                flowchart LR
                
                A[Arrival]--> B[Advice]
                
                B -.-> F([Nurse/Cubicle])
                F -.-> B
                
                B----> |30% of patients| C[Treatment]

                C -.-> G([Nurse/Cubicle])
                G -.-> C

                B ----> |70% of patients| Z[Discharge]
                C --> Z

                classDef default font-size:18pt,font-family:lexend;
                linkStyle default stroke:white;
            """
        )

with tab2:
    st.markdown(read_file_contents('resources/entity_paths_text.md'))

with tab3:
    st.markdown("Placeholder")

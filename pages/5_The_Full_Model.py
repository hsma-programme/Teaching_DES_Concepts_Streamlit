'''
A Streamlit application based on Monks and 

Allows users to interact with an increasingly more complex treatment simulation 
'''
import streamlit as st

from helper_functions import read_file_contents, add_logo, mermaid
from model_classes import *
# from st_pages import show_pages_from_config, add_page_title

st.set_page_config(
     page_title="The Full Model",
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
st.subheader("How can we optimise the full system?")

tab1, tab2, tab3 = st.tabs(["Introduction", "Exercises", "Playground"])
with tab1:
    st.markdown("""
                So now we have explored every component of the model:
                - Generating arrivals
                - Generating and using resources
                - Sending people down different paths 
                
                It's time to bring it all together into the final version of the treatment centre model we saw at the beginning.
                """
                )
    
    mermaid(height=450, code=
    """
    %%{ init: { 'flowchart': { 'curve': 'step', "defaultRenderer": "elk" } } }%%
    %%{ init: {  'theme': 'base', 'themeVariables': {'lineColor': '#b4b4b4'} } }%%
    flowchart LR
        A[Arrival] --> B{Trauma or non-trauma}
        B --> C[Stabilisation]
        C --> E[Treatment]
      
        B --> D[Registration]
        D --> G[Examination]

        G --> H[Treat?]
        H --> F 

        H --> I[Non-Trauma Treatment]
        I --> F 

        C --> Z([Trauma Room])
        Z --> C

        E --> Y([Cubicle - 1])
        Y --> E

        D --> X([Clerks])
        X --> D

        G --> W([Exam Room])
        W --> G

        I --> V([Cubicle - 2])
        V --> I

        E --> F[Discharge]

        classDef ZZ1 fill:#47D7FF,font-family:lexend
        classDef ZZ2 fill:#5DFDA0,font-family:lexend
        classDef ZZ2a fill:#02CD55,font-family:lexend, color:#FFF
        classDef ZZ3 fill: #D45E5E,font-family:lexend
        classDef ZZ3a fill: #932727,font-family:lexend, color:#FFF
        classDef ZZ4 fill: #611D67,font-family:lexend, color:#FFF

        class A,B ZZ1
        class C,E ZZ2
        class D,G ZZ3
        class X,W ZZ3a
        class Z,Y ZZ2a
        class I,V ZZ4;
    """
)
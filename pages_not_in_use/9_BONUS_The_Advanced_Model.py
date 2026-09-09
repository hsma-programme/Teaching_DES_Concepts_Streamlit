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

mermaid(height=800, code=
"""
    %%{ init: { 'flowchart': { 'curve': 'step'} } }%%
    %%{ init: {  'theme': 'base', 'themeVariables': {'lineColor': '#b4b4b4'} } }%%
    flowchart LR
        A[Arrival] --> B{Trauma or non-trauma}
        B --> B1{Trauma Pathway} 
        B --> B2{Non-Trauma Pathway}
        
        B1 --> C[Stabilisation]
        C --> E[Treatment]
      
        B2 --> D[Registration]
        D --> G[Examination]

        G --> H[Treat?]
        H ----> F 

        H --> I[Non-Trauma Treatment]
        I --> F 

        C -.-> Z([Trauma Room\n<b>RESOURCE</b>])
        Z -.-> C
        C -.-> Z2([Nurse\n<b>RESOURCE</b>])
        Z2 -.-> C

        E -.-> Y([Cubicle - 1\n<b>RESOURCE</b>])
        Y -.-> E
        E -.-> Y2([Nurse\n<b>RESOURCE</b>])
        Y2 -.-> E

        D -.-> X([Clerks\n<b>RESOURCE</b>])
        X -.-> D

        G -.-> W([Exam Room\n<b>RESOURCE</b>])
        W -.-> G
        G -.-> W2([Nurse\n<b>RESOURCE</b>])
        W2 -.-> G

        I -.-> V([Cubicle - 2\n<b>RESOURCE</b>])
        V -.-> I
        I -.-> V2([Nurse\n<b>RESOURCE</b>])
        V2 -.-> I

        E ----> F[Discharge]

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

import streamlit as st
from helper_functions import read_file_contents, add_logo, mermaid
# from st_pages import show_pages_from_config, add_page_title

st.set_page_config(
    page_title="Introduction",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# add_page_title()

# show_pages_from_config()

add_logo()

with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

st.title("Welcome to the Discrete Event Simulation Playground! 👋")

st.markdown(read_file_contents('resources/introduction_text.md'))


mermaid(height=450, code=
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

        E -.-> Y([Cubicle - 1\n<b>RESOURCE</b>])
        Y -.-> E

        D -.-> X([Clerks\n<b>RESOURCE</b>])
        X -.-> D

        G -.-> W([Exam Room\n<b>RESOURCE</b>])
        W -.-> G

        I -.-> V([Cubicle - 2\n<b>RESOURCE</b>])
        V -.-> I

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

st.markdown(
"""
## References

1. *Monks.T, Harper.A, Anagnoustou. A, Allen.M, Taylor.S. (2022) Open Science for Computer Simulation*
2. *Nelson. B.L. (2013). [Foundations and methods of stochastic simulation](https://www.amazon.co.uk/Foundations-Methods-Stochastic-Simulation-International/dp/1461461596/ref=sr_1_1?dchild=1&keywords=foundations+and+methods+of+stochastic+simulation&qid=1617050801&sr=8-1). Springer.* 
3. https://health-data-science-or.github.io/simpy-streamlit-tutorial/
"""    
)



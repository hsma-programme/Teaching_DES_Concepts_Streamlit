import streamlit as st
from helper_functions import read_file_contents, add_logo, mermaid

st.set_page_config(
    page_title="Introduction",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded",
)

add_logo()

st.title("Welcome to the Discrete Event Simulation Playground! 👋")

st.markdown(read_file_contents('resources/introduction_text.md'))


mermaid(height=450, code=
"""
    flowchart LR
        A[Arrival] --> B{Trauma or non-trauma}
        B --> C[Stabilisation]
        C --> E[Treatment]
        E --> F[Discharge]
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



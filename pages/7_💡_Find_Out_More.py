'''
A page containing information about

---

A Streamlit application based on the open treatment centre simulation model from Monks.T, Harper.A, Anagnoustou. A, Allen.M, Taylor.S. (2022)

Original Model: https://github.com/TomMonks/treatment-centre-sim/tree/main

Allows users to interact with an increasingly complex treatment centre simulation
'''
import gc
import streamlit as st

from helper_functions import add_logo

st.set_page_config(
     page_title="Find Out More",
     layout="wide",
     initial_sidebar_state="expanded",
 )

add_logo()

with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

## We add in a title for our web app's page
st.title("Discrete Event Simulation Playground")

st.subheader("Simulation Modelling in the HSMA")

gc.collect()

st.markdown(
    """
    Joining the HSMA programme will give you access to
    - three sessions on discrete event simulation
    - a session on system dynamics modelling (for large, system-scale problems)
    - sessions on cellular automata and agent-based simulation (for modelling interactions and motivations of individuals that lead to high-level patterns, e.g. to look at the spread of disease)
    - sessions on creating web-based interfaces (like this one!) for allowing users to interact with your models
    """
)


st.subheader("Where Can I Find Out More?")

st.markdown(
    """
    If you just can't wait until the next round of HSMA, you can access the previous videos on discrete event simulation below.

    However - if you apply to HSMA 6, you will get the benefit of support from the HSMA team as well as a peer support group.

    We're always revising our content, so HSMA 6 will be bigger and better than ever before!
    """
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Video 1")
    st.video("https://www.youtube.com/watch?v=IlUPJcowBrA")

with col2:
    st.subheader("Video 2")
    st.video("https://www.youtube.com/watch?v=F3av_4iJMzA")


st.markdown(
    """
    Several HSMA projects have made use of discrete event simulation to motivate incredible changes in health systems.
    """
)


st.markdown(
    """

    Finally, this whole exercise website has been written in Streamlit - another topic we cover on the course!
    Streamlit allows you to create highly customisable websites that allow you to share results with users and give them the freedom to interact with powerful Python code without needing Python on their own computers.

    Two brand new sessions on Streamlit are being created for HSMA 6 - so apply now if you want to find out more!
    """
)

st.subheader("Where Can I Find the Code for this Model?")

st.markdown("All of the code used to make this model, the visualisation and the streamlit app can be found in [this GitHub repository](https://github.com/hsma-programme/Teaching_DES_Concepts_Streamlit).")

st.markdown("The code is available under the MIT licence so may be freely used and adapted - though we'd love to hear about it if you do use the app or code!")

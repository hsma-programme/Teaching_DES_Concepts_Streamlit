'''
A Streamlit application based on Monks and 

Allows users to interact with an increasingly more complex treatment simulation 
'''
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

st.subheader("Simulation Modelling in the HSMA")

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
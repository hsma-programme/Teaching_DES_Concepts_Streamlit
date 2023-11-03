import streamlit as st
import pandas as pd

from helper_functions import read_file_contents, add_logo, mermaid
from model_classes import *
# from st_pages import show_pages_from_config, add_page_title
import plotly.express as px


st.set_page_config(
     page_title="The Full Model",
     layout="wide",
     initial_sidebar_state="expanded",
 )

# Initialise session state
if 'session_results' not in st.session_state:
    st.session_state['session_results'] = []

# add_page_title()

# show_pages_from_config()

add_logo()

with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)
    

## We add in a title for our web app's page
st.title("Discrete Event Simulation Playground")
st.subheader("How can we optimise the full system?")

if len(st.session_state['session_results']) > 0:

    all_run_results = pd.concat(st.session_state['session_results'])

    st.subheader("Look at Average Results Across Replications")

    st.write(all_run_results.groupby('Model Run').median().T)

    col_res_1, col_res_2 = st.columns(2)

    

    with col_res_1:
        st.subheader("Utilisation Metrics")

        st.plotly_chart(px.box(
            all_run_results.reset_index().melt(id_vars=["Model Run", "rep"]).set_index('variable').filter(like="util", axis=0).reset_index(), 
            y="variable", 
            x="value",
            color="Model Run",
            points="all",
            range_x=[0, 1]),
            use_container_width=True
            )
        
        # st.write(all_run_results.filter(like="util", axis=1).merge(all_run_results.filter(like="throughput", axis=1),left_index=True,right_index=True))
        
    with col_res_2:
        st.subheader("Wait Metrics")
        # Add in a box plot showing waits
        st.plotly_chart(px.box(
            all_run_results.reset_index().melt(id_vars=["Model Run", "rep"]).set_index('variable').filter(like="wait", axis=0).reset_index(), 
        #                 left_index=True, right_index=True), 
            y="variable", 
            x="value",
            color="Model Run",
            points="all"),
            use_container_width=True
            )

    col_res_3, col_res_4 = st.columns(2)

    with col_res_3:
        st.subheader("Throughput")
        # Add in a box plot showing waits
        st.plotly_chart(px.box(
            all_run_results.reset_index().melt(id_vars=["Model Run", "rep"]).set_index('variable').filter(like="throughput", axis=0).reset_index(),  
            y="variable", 
            x="value",
            color="Model Run",
            points="all"),
            use_container_width=True
            )

        # st.write(all_run_results.filter(like="wait", axis=1)
        #             .merge(all_run_results.filter(like="throughput", axis=1), 
        #                 left_index=True, right_index=True))
else:
    st.markdown("No scenarios yet run. Go to 'The Full Model' page.")
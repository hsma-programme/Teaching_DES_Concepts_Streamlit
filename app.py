'''
A Streamlit application based on Monks and 

Allows users to interact with an increasingly more complex treatment simulation 
'''
import streamlit as st

from helper_functions import read_file_contents
from model_classes import *


st.set_page_config(
     page_title="Urgent Care Sim App",
     layout="wide",
     initial_sidebar_state="expanded",
 )

## We add in a title for our web app's page
st.title("Urgent care call centre")

st.markdown(read_file_contents('resources/model_info.md'))

tab1, tab2, tab3 = st.tabs(["Generating Patients", 
                            "Allocating Patients to A Nurse", 
                            "Different Types of Patients"])

with tab1:
    

    col1_1, col1_2, col1_3 = st.columns(3)
    # set number of resources
    with col1_1:
        mean_arrivals_per_day = st.slider("How many patients should arrive per day on average?", 
                                          10, 1000, 
                                          step=5)
        # Will need to convert mean arrivals per day into interarrival time and share that

    with col1_2:
    # set number of replications
        n_reps = st.slider("How many times should the simulation run?", 
                           1, 50, 
                           step=1)

    with col1_3:
    # set days to include
        run_time_days = st.slider("How many days should we run the simulation for each time?", 
                             1, 100, 
                             step=1)

    args = Scenario()

     # A user must press a streamlit button to run the model
    if st.button("Run simulation"):

        # add a spinner and then display success box
        with st.spinner('Simulating the minor injuries unit...'):
            # run multiple replications of experment
            results = multiple_replications(
                args, 
                n_reps=n_reps, 
                rc_period=run_time_days*60*24
                )

        st.success('Done!')
        

        st.table(pd.concat([
            results[['00_arrivals']].astype('int'),
            (results[['00_arrivals']]/run_time_days).round(0).astype('int')
        ], axis=1, keys = ['TotalArrivals', 'Mean Daily Arrivals'])
            )

        

'''
A Streamlit application based on Monks and 

Allows users to interact with an increasingly more complex treatment simulation 
'''
import time
import streamlit as st

from helper_functions import read_file_contents
from model_classes import *


st.set_page_config(
     page_title="Urgent Care Sim App",
     layout="wide",
     initial_sidebar_state="expanded",
 )

## We add in a title for our web app's page
st.title("Treatment Centre Simulation Playground")

st.markdown(read_file_contents('resources/model_info.md'))

tab1, tab2, tab3 = st.tabs(["Generating Patients", 
                            "Allocating Patients to A Nurse", 
                            "Different Types of Patients"])

with tab1:
    

    col1_1, col1_2, col1_3, col1_4 = st.columns([2, 2, 2 , 1])
    # set number of resources
    with col1_1:
        mean_arrivals_per_day = st.slider("How many patients should arrive per day on average?", 
                                          10, 1000, 
                                          step=5, value=300)
        # Will need to convert mean arrivals per day into interarrival time and share that

    with col1_2:
    # set number of replications
        n_reps = st.slider("How many times should the simulation run?", 
                           1, 50, 
                           step=1, value=10)

    with col1_3:
    # set days to include
        run_time_days = st.slider("How many days should we run the simulation for each time?", 
                             1, 100, 
                             step=1, value=15)
        
    with col1_4:
    # set days to include
        seed = st.number_input("Set a random number for the computer to start from", 
                             1, 100000,
                             step=1, value=42)

    args = Scenario(random_number_set=seed)

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

        st.subheader("Total Number of Patients Generated per Simulation Run")

        progress_bar = st.progress(0)
        status_text = st.text(
            'The first simulation generated a total of {} patients (an average of {} patients per day)'
            .format(results[['00_arrivals']].iloc[0]['00_arrivals'].astype(int), 
                    (results[['00_arrivals']].iloc[0]['00_arrivals']/run_time_days).round(1)
                    )
                    )
        
        chart_mean_daily = st.bar_chart(results[['00_arrivals']].iloc[[0]]/run_time_days)
        #chart_total = st.bar_chart(results[['00_arrivals']].iloc[[0]])
        

        for i in range(n_reps-1):
        # Update progress bar.
            #progress_bar.progress(n_reps/(i+1))
            time.sleep(1)
            new_rows = results[['00_arrivals']].iloc[[i+1]]

            #Update status text.
            status_text.text(
                'The next simulation generated a total of {} patients (an average of {} patients per day)'.format(
                    new_rows.iloc[0]['00_arrivals'].astype(int),
                    (new_rows.iloc[0]['00_arrivals']/run_time_days).round(1)
                )
                )

            # Append data to the chart.
            #chart_total.add_rows(new_rows)
            chart_mean_daily.add_rows(new_rows/run_time_days)

            # Pretend we're doing some computation that takes time.
            #time.sleep(0.5)


        st.table(pd.concat([
                results[['00_arrivals']].astype('int'),
                (results[['00_arrivals']]/run_time_days).round(0).astype('int')
            ], axis=1, keys = ['Total Arrivals', 'Mean Daily Arrivals'])
                )
    
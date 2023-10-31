'''
A Streamlit application based on Monks and 

Allows users to interact with an increasingly more complex treatment simulation 
'''
import time
import streamlit as st
import numpy as np
import plotly.express as px

from helper_functions import read_file_contents, add_logo, mermaid
from model_classes import Scenario, multiple_replications
from distribution_classes import Exponential
# from st_pages import show_pages_from_config, add_page_title

st.set_page_config(
    page_title="Simulating Arrivals",
    layout="wide",
    initial_sidebar_state="expanded",
)

# add_page_title()

# show_pages_from_config()

add_logo()

with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# We add in a title for our web app's page
st.title("Discrete Event Simulation Playground")
st.subheader("Simulating Patients Arriving at the Centre")

tab1, tab2, tab3 = st.tabs(["Introduction", "Exercise", "Playground"])

with tab1:

    st.markdown(
        "Let's start with just having some patients arriving into our treatment centre.")

    mermaid(height=250, code="""
            %%{ init: {  'flowchart': { 'curve': 'step', "defaultRenderer": "elk" } } }%%

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

            classDef highlight fill:#02CD55,stroke:#E8AD02,stroke-width:4px,color:#0C0D11,font-size:12pt,font-family:lexend;
            classDef unlight fill:#b4b4b4,stroke:#787878,stroke-width:2px,color:#787878,font-size:6pt,font-family:lexend;

            class A highlight;
            class B,B1,B2,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z unlight;

            
        """
            )
    
    st.markdown(
    """
    To start with, we need to create some simulated patients who will turn up to our centre. 

    To simulate patient arrivals, we will use the exponential distribution. 

    """
    )
    
    exp_dist = Exponential(mean=5)
    st.plotly_chart(px.histogram(exp_dist.sample(size=2500), 
                                 width=600, height=300))

    st.markdown(read_file_contents('resources/simulating_arrivals_text.md'))

    st.divider()


with tab2:

    st.subheader("Things to Try Out")

    st.markdown(

        """
        - Try changing the random number the computer uses without changing anything else. What happens to the number of patients? Does the animated bar chart look different?
        - Try increasing the simulation runs. What happens to the shape of the histograms?
        - Try running the simulation for fewer days. What happens to the animated bar chart compared to running the simulation for more days?
        - Look at the scatter (dot) plots at the bottom of the page to understand how the arrival times of patients varies across different simulation runs and different days. 
        """

    )

with tab3:
    col1_1, col1_2= st.columns([0.5, 1.5])
    # set number of resources
    with col1_1:
        seed = st.number_input("Set a random number for the computer to start from",
                        1, 100000,
                        step=1, value=42)
        
        n_reps = st.slider("How many times should the simulation run?",
                           1, 30,
                           step=1, value=10)
        run_time_days = st.slider("How many days should we run the simulation for each time?",
                                  1, 60,
                                  step=1, value=15)

     
        mean_arrivals_per_day = st.slider("How many patients should arrive per day on average?",
                                          10, 1000,
                                          step=5, value=300)
        # Will need to convert mean arrivals per day into interarrival time and share that
        exp_dist = Exponential(mean=60/(mean_arrivals_per_day/24), random_seed=seed)
        st.plotly_chart(px.histogram(exp_dist.sample(size=2500), 
                                width=500, height=250,
                                labels={
                     "value": "Inter-Arrival Time (Minutes)",
                     "count": " "
                 }))

        # set number of replication
with col1_2:     
    args = Scenario(random_number_set=seed, 
                    # We want to pass the interarrival time here
                    # To get from daily arrivals to average interarrival time,
                    # divide the number of arrivals by 24 to get arrivals per hour,
                    # then divide 60 by this value to get the number of minutes
                    manual_arrival_lambda=60/(mean_arrivals_per_day/24),
                    override_arrival_lambda=True)

    # A user must press a streamlit button to run the model
    button_run_pressed = st.button("Run simulation")
    
    if button_run_pressed:

        # add a spinner and then display success box
        with st.spinner('Simulating the minor injuries unit...'):
            # run multiple replications of experment
            results = multiple_replications(
                args,
                n_reps=n_reps,
                rc_period=run_time_days*60*24
            )

            patient_log = multiple_replications(
                args,
                n_reps=n_reps,
                rc_period=run_time_days*60*24,
                return_full_log=False,
                return_event_log=True
            )
            patient_log = patient_log.assign(model_day = (patient_log.time/24/60).pipe(np.floor)+1)
            patient_log = patient_log.assign(time_in_day= (patient_log.time - ((patient_log.model_day -1) * 24 * 60)).pipe(np.floor))
            # patient_log = patient_log.assign(time_in_day_ (patient_log.time_in_day/60).pipe(np.floor))
            patient_log['patient_full_id'] = patient_log['Rep'].astype(str) + '_' + patient_log['patient'].astype(str) 
            patient_log['rank'] = patient_log['time_in_day'].rank(method='max')

        #st.success('Done!')

        st.subheader(
            "Difference between average daily patients generated in first simulation run and subsequent simulation runs"
            )

        #progress_bar = st.progress(0)

        # chart_mean_daily = st.bar_chart(results[['00_arrivals']].iloc[[0]]/run_time_days)
        chart_mean_daily = st.bar_chart(
            results[['00_arrivals']].iloc[[0]]/
            run_time_days - results[['00_arrivals']].iloc[[0]]/run_time_days,

            height=250
            
            )
        # chart_total = st.bar_chart(results[['00_arrivals']].iloc[[0]])

        status_text_string = 'The first simulation generated a total of {} patients (an average of {} patients per day)'.format(
            results[['00_arrivals']].iloc[0]['00_arrivals'].astype(int),
            (results[['00_arrivals']].iloc[0]
            ['00_arrivals']/run_time_days).round(1)
        )
        status_text = st.text(status_text_string)

        for i in range(n_reps-1):
            # Update progress bar.
            # progress_bar.progress(n_reps/(i+1))
            time.sleep(0.5)
            new_rows = results[['00_arrivals']].iloc[[i+1]]

            # Append data to the chart.
            # chart_total.add_rows(new_rows)
            # chart_mean_daily.add_rows(new_rows/run_time_days)
            chart_mean_daily.add_rows(
                ((results[['00_arrivals']].iloc[[i+1]]['00_arrivals']/run_time_days) -
                (results[['00_arrivals']].iloc[0]['00_arrivals']/run_time_days)).round(1)
            )

            status_text_string = 'Simulation {} generated a total of {} patients (an average of {} patients per day)'.format(
                    i+2,
                    new_rows.iloc[0]['00_arrivals'].astype(int),
                    (new_rows.iloc[0]['00_arrivals']/run_time_days).round(1)
                ) + "\n" + status_text_string 
            # Update status text.
            status_text.text(status_text_string)

        # st.table(pd.concat([
        #         results[['00_arrivals']].astype('int'),
        #         (results[['00_arrivals']]/run_time_days).round(0).astype('int')
        #     ], axis=1, keys = ['Total Arrivals', 'Mean Daily Arrivals'])
        #         )
if button_run_pressed:
    col_a_1, col_a_2 = st.columns(2)

    with col_a_1:
        st.subheader(
            "Histogram: Total Patients per Run"
        )

        st.plotly_chart(
            px.histogram(
                results[['00_arrivals']]
                )
        )
        
    with col_a_2:
        st.subheader(
                "Histogram: Average Daily Patients per Run"
        )

        st.plotly_chart(
            px.histogram(
                (results[['00_arrivals']]/run_time_days).round(1)
                )
        )
    

    
    #st.write(patient_log)

    # Animated chart - 
    # st.plotly_chart(px.scatter(
    #     patient_log,
    #     #patient_log[patient_log['event'] == 'arrival'], 
    #     x="time_in_day", 
    #     y="Rep", 
    #     animation_frame="rank", 
    #     animation_group="patient",
    #     #size="pop", 
    #     #color="Rep", 
    #     #hover_name="patient",
    #     #log_x=True, 
    #     #size_max=55, 
    #     range_x=[0, 24*60], 
    #     range_y=[0,n_reps+1]))

    st.markdown(
        """
        The plots below show the minute-by-minute arrivals of patients across different model replications and different days.
        Only the first 10 replications and a maximum of 30 days are shown.

        Each dot is a single patient arriving.

        From left to right within each plot, we start at one minute past midnight and move through the day until midnight. 

        Looking from the top to the bottom of each plot, we have the model replications. 
        Each horizontal line represents a **full day** for one model replication.  
        """ 
    )

    #facet_col_wrap_calculated = np.ceil(run_time_days/4).astype(int)

    st.plotly_chart(px.scatter(
            patient_log[(patient_log['event'] == 'arrival') & 
                        (patient_log['Rep'] <= 10) & 
                        (patient_log['model_day'] <= 30)],
            #patient_log,
            x="time_in_day", 
            y="Rep",
            range_x=[0, 24*60], 
            range_y=[0, min(10, n_reps)+1],
            facet_col='model_day', 
            # facet_col_wrap=facet_col_wrap_calculated, # this causes an unbound_local_error when used so hard coding for now
            facet_col_wrap = 4,
            width=1200,
            height=1500
    ), use_container_width=True)




        


    # st.print(
    #     results[['10_full_patient_df']]
    # )


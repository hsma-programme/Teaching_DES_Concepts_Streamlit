'''
A Streamlit application based on Monks and 

Allows users to interact with an increasingly more complex treatment simulation 
'''
import time
import streamlit as st
import plotly.express as px

from helper_functions import read_file_contents, add_logo, mermaid
from model_classes import Scenario, multiple_replications
from distribution_classes import Exponential


st.set_page_config(
    page_title="Simulating Arrivals",
    layout="wide",
    initial_sidebar_state="expanded",
)

add_logo()


with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# We add in a title for our web app's page
st.title("Discrete Event Simulation Playground")
st.subheader("Simulating Patients Arriving at the Centre")

tab1, tab2 = st.tabs(["Introduction", "Exercise"])

with tab1:

    st.markdown(
        "Let's start with just having some patients arriving into our treatment centre.")

    mermaid(height=250, code="""
            %%{ init: {  'flowchart': { 'curve': 'step', "defaultRenderer": "elk" } } }%%

            %%{ init: {  'theme': 'base', 'themeVariables': {'lineColor': '#b4b4b4'} } }%%
            flowchart LR

            A[Arrival]:::highlight --> B{Trauma or non-trauma} 
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

            classDef highlight fill:#02CD55,stroke:#E8AD02,stroke-width:4px,color:#0C0D11,font-size:12pt,font-family:lexend;
            classDef unlight fill:#b4b4b4,stroke:#787878,stroke-width:2px,color:#787878,font-size:6pt,font-family:lexend;

            class A highlight;
            class B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z unlight;

            
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
    col1_1, col1_2= st.columns([0.5, 1.5])
    # set number of resources
    with col1_1:
        seed = st.number_input("Set a random number for the computer to start from",
                        1, 100000,
                        step=1, value=42)
        
        n_reps = st.slider("How many times should the simulation run?",
                           1, 50,
                           step=1, value=10)
        run_time_days = st.slider("How many days should we run the simulation for each time?",
                                  1, 100,
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
    if st.button("Run simulation"):

        # add a spinner and then display success box
        with st.spinner('Simulating the minor injuries unit...'):
            # run multiple replications of experment
            results = multiple_replications(
                args,
                n_reps=n_reps,
                rc_period=run_time_days*60*24
            )

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


    # st.print(
    #     results[['10_full_patient_df']]
    # )


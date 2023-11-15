'''
A Streamlit application based on Monks and 

Allows users to interact with an increasingly more complex treatment simulation 
'''
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from output_animation_functions import reshape_for_animations, animate_queue_activity_bar_chart, animate_activity_log
import asyncio

from helper_functions import read_file_contents, add_logo, mermaid
from model_classes import Scenario, multiple_replications
# from st_pages import show_pages_from_config, add_page_title

# Set page parameters
st.set_page_config(
     page_title="Using a Simple Resource",
     layout="wide",
     initial_sidebar_state="expanded",
 )

# add_page_title()

# show_pages_from_config()

# Add the logo
add_logo()
# Import the stylesheet
with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)


st.title("Discrete Event Simulation Playground")
st.subheader("Using a Simple Resource: Sending Patients to be Treated")

tab1, tab2, tab3 = st.tabs(["Introduction", "Exercise", "Playground"])

with tab1:

    st.markdown(
        """
        Now, it's all well and good having patients arrive, but at the moment there is no-one and nowhere to see them!

    We need to add our first resource.

    Resources exist inside our simulation, and can be nurses, rooms, ambulances - whatever we need them to be. 

    When someone reaches the front of the queue, they will be allocated to a resource that is currently free.
    They will hold onto this resource for as long as they need it, and then they will let go of it and move on to the next part of the process.

    This means resources can continue to be reused again and again in the system, unlike our arrivals.

    So for now, let's make it so that when someone arrives, they need to be treated, and to do this they will need a resource.
    For now, we're keeping it simple - let's assume each nurse has a room that they treat people in. They always stay in this room, and as soon as a patient has finished being treated, the patient will leave and the nurse (and room) will become available again.

    This means we just have one type of resource to worry about. 
    """
    )

    mermaid(height=175, code=
    """
            %%{ init: { 'flowchart': { 'curve': 'step' } } }%%
            %%{ init: {  'theme': 'base', 'themeVariables': {'lineColor': '#b4b4b4'} } }%%
            flowchart LR
            A[Arrival]----> B[Treatment]
            B -.-> C([Nurse/Cubicle\n<b>RESOURCE</b>])
            C -.-> B
            B ----> F[Discharge]

            classDef default font-size:18pt,font-family:lexend;
            linkStyle default stroke:white;
        """
    )

    st.markdown(
"""
For now, we'll assume all of our patients are roughly equally injured - but there might still be some variation in how long it takes to treat them. Some might need a few stitches, some might just need a quick bit of advice. 

This time, we're going to sample from a different distribution - the normal distribution. A few people won't take very long to fix up, while a few might take quite a long time - but most of the people will take an amount of time that's somewhere in the middle. 

[ADD EXAMPLE NORMAL DISTRIBUTION]

We're going to start measuring a few more things now
- how much of each resource's time is spent with patients **(known as resource utilisation)**
- how long each patient waits before they get allocated a resource
- what percentage of patients meet a target of being treated within 2 hours of turning up to our treatment centre
"""


    )

with tab2:
    st.markdown(
"""
### Things to Try Out

- Keeping the default values, run the model and take a look at the animated flow of patients through the system. What do you notice about
    - the number of nurses in use
    - the size of the queue for treatmetn at different times

- What happens when you play around with the number of nurses we have available? 
    - Look at the queues, but look at the resource utilisation too. The resource utilisation tells us how much of the time each nurse is busy rather than waiting for a patient to turn up. 
    - Can you find a middle ground where the nurse is being used a good amount without the queues building up?

- What happens to the average utilisation and waits when you change 
    - the average length of time it takes each patient to be seen?
    - the variability in the length of time it takes each patient to be seen?

"""
    )


with tab3:
    col1, col2 = st.columns([0.5, 1.5])

    with col1:
        nurses = st.slider("How Many Rooms/Nurses Are Available?", 1, 10, step=1, value=7)

        consult_time = st.slider("How long (in minutes) does a consultation take on average?",
                                    5, 120, step=5, value=50)

        consult_time_sd = st.slider("How much (in minutes) does the time for a consultation usually vary by?",
                                    5, 30, step=5, value=10)

        
        with st.expander("Previous Parameters"):

            st.markdown("If you like, you can edit these parameters too!")

            seed = st.number_input("Set a random number for the computer to start from",
                            1, 10000000,
                            step=1, value=42)
            
            n_reps = st.slider("How many times should the simulation run?",
                            1, 30,
                            step=1, value=10)
            
            run_time_days = st.slider("How many days should we run the simulation for each time?",
                                    1, 60,
                                    step=1, value=15)

        
            mean_arrivals_per_day = st.slider("How many patients should arrive per day on average?",
                                            10, 500,
                                            step=5, value=300)

    with col2:
        args = Scenario(
                random_number_set=seed,
                n_cubicles_1=nurses,
                override_arrival_lambda=True,
                manual_arrival_lambda=60/(mean_arrivals_per_day/24),
                model="simplest",
                trauma_treat_mean=consult_time,
                trauma_treat_var=consult_time_sd
                )

        # A user must press a streamlit button to run the model
        button_run_pressed = st.button("Run simulation")
        
        
        if button_run_pressed:

            # add a spinner and then display success box
            with st.spinner('Simulating the minor injuries unit...'):
                await asyncio.sleep(0.1)
                # run multiple replications of experment
                detailed_outputs = multiple_replications(
                    args,
                    n_reps=n_reps,
                    rc_period=run_time_days*60*24,
                    return_detailed_logs=True
                )

                results = pd.concat([detailed_outputs[i]['results']['summary_df'].assign(rep= i+1)
                                            for i in range(n_reps)]).set_index('rep')
                
                full_event_log = pd.concat([detailed_outputs[i]['results']['full_event_log'].assign(rep= i+1)
                                            for i in range(n_reps)])
                

                st.plotly_chart(px.box(
                    results.reset_index().melt(id_vars=["rep"]).set_index('variable').filter(like="util", axis=0).reset_index(), 
                    y="variable", 
                    x="value",
                    points="all",
                    range_x=[0, 1.1],
                    height=200),
                    use_container_width=True
                )

                st.plotly_chart(px.box(
                    results.reset_index().melt(id_vars=["rep"]).set_index('variable').filter(like="wait", axis=0).reset_index(), 
                    y="variable", 
                    x="value",
                    points="all",
                    height=200,
                    range_x=[0, results.reset_index().melt(id_vars=["rep"]).set_index('variable').filter(like="wait", axis=0).reset_index().max().value]
                    ),
                    use_container_width=True
                )

                st.plotly_chart(px.box(
                    results.reset_index().melt(id_vars=["rep"]).set_index('variable').filter(like="throughput", axis=0).reset_index(), 
                    y="variable", 
                    x="value",
                    points="all",
                    height=200,
                    range_x=[0, results.reset_index().melt(id_vars=["rep"]).set_index('variable').filter(like='throughput', axis=0).reset_index().max().value]
                    ),
                    use_container_width=True
                )

               

            event_position_df = pd.DataFrame([
                            {'event': 'arrival', 'x':  50, 'y': 300, 'label': "Arrival" },
                            
                            # Triage - minor and trauma                
                            {'event': 'treatment_wait_begins', 'x':  150, 'y': 200, 'label': "Waiting for Treatment"  },
                            {'event': 'treatment_begins', 'x':  250, 'y': 100, 'resource':'n_cubicles_1', 'label': "Being Treated" },
                        
                        ])
            animation_dfs_log = reshape_for_animations(
                        full_event_log=full_event_log[
                            (full_event_log['rep']==1) &
                            ((full_event_log['event_type']=='queue') | (full_event_log['event_type']=='resource_use')  | (full_event_log['event_type']=='arrival_departure'))
                        ]
                    )
    if button_run_pressed:
        st.subheader("Animated Model Output")
        with st.spinner('Generating the animated patient log...'):
            st.plotly_chart(animate_activity_log(
                                animation_dfs_log['full_patient_df'],
                                event_position_df = event_position_df,
                                scenario=args,
                                include_play_button=True,
                                return_df_only=False,
                                plotly_height=500,
                                wrap_queues_at=10,
                                time_display_units="dhm"
                        ), use_container_width=True)

            # st.write(results)


            # st.write(full_event_log)
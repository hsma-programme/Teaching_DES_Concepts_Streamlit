'''
A Streamlit application based on Monks and 

Allows users to interact with an increasingly more complex treatment simulation 
'''
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import asyncio

from output_animation_functions import reshape_for_animations,animate_activity_log
from helper_functions import add_logo, mermaid
from model_classes import Scenario, multiple_replications

st.set_page_config(
     page_title="Adding an Optional Step",
     layout="wide",
     initial_sidebar_state="expanded",
 )

# show_pages_from_config()

add_logo()

with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

## We add in a title for our web app's page
st.title("Discrete Event Simulation Playground")
st.subheader("Making Patients Behave Differently: Adding in an Optional Step")

tab1, tab2, tab3 = st.tabs(["Introduction", "Exercise", "Playground"])

with tab1:

    st.markdown("""
                Now, it's not as simple as all of our patients being looked at by a nurse and then sent on their merry way.

                Some of them - but not all of them - may require another step where they undergo some treatment.
                
                So for some people, their pathway looks like this:
                """)


    mermaid(height=225, code=
        """
                %%{ init: { 'flowchart': { 'curve': 'step' } } }%%
                %%{ init: {  'theme': 'base', 'themeVariables': {'lineColor': '#b4b4b4'} } }%%
                flowchart LR
                
                A[Arrival]----> B[Advice]
                
                B -.-> F([Nurse/Cubicle])
                F -.-> B
                
                B----> C[Treatment]

                C -.-> G([Nurse/Cubicle])
                G -.-> C

                C ----> Z[Discharge]

                classDef default font-size:18pt,font-family:lexend;
                linkStyle default stroke:white;
            """
        )

    st.markdown("But for other simpler cases, their pathway still looks like this!")

    mermaid(height=225, code=
        """
                %%{ init: { 'flowchart': { 'curve': 'step' } } }%%
                %%{ init: {  'theme': 'base', 'themeVariables': {'lineColor': '#b4b4b4'} } }%%
                flowchart LR
                
                A[Arrival]----> B[Advice]
                
                B -.-> F([Nurse/Cubicle])
                F -.-> B
                
                B ----> Z[Discharge]

                classDef default font-size:18pt,font-family:lexend;
                linkStyle default stroke:white;
            """
        )

    st.markdown(
        """
        So how do we ensure that some of our patients go down one pathway and not the other?

        You guessed it - the answer is sampling from a distribution again! 

        We can tell the computer the rough split we'd like to say - let's say 30% of our patients need the treatment step, but the other 70% will 

        And as before, there will be a bit of randomness, just like in the real world.
        In one simulation, we might end up with a 69/31 split, and the next might be 72/28, but it will always be around the expected split we've asked for.
        """
    )

    st.markdown(
        """
        We can think of our pathway as looking like this overall:
        """
    )

    mermaid(height=225, code=
        """
                %%{ init: { 'flowchart': { 'curve': 'step' } } }%%
                %%{ init: {  'theme': 'base', 'themeVariables': {'lineColor': '#b4b4b4'} } }%%
                flowchart LR
                
                A[Arrival]--> B[Advice]
                
                B -.-> F([Nurse/Cubicle])
                F -.-> B
                
                B----> |30% of patients| C[Treatment]

                C -.-> G([Nurse/Cubicle])
                G -.-> C

                B ----> |70% of patients| Z[Discharge]
                C --> Z

                classDef default font-size:18pt,font-family:lexend;
                linkStyle default stroke:white;
            """
        )

with tab2:
    st.markdown(
    """
### Things to Try Out

- What impact does changing the number of patients who go down this extra route have on our treatment centre?

- What if we change the number of nurses at each step?

- What if we make it so any nurse who is free can be picked up for this stage rather than having two separate pools of nurses?
    """
    )

with tab3:

    col1, col2 = st.columns([1,3])

    with col1:
        treat_p = st.slider("Probability that a patient will need treatment", 0.0, 1.0, step=0.01, value=0.7)

        nurses_floating_resource = st.checkbox("Tick this box to make any nurse able to be used at any point in the process.")

        if not nurses_floating_resource:
            nurses_advice = st.slider("How Many Nurses are Available for Advice?", 1, 10, step=1, value=3)
            nurses_treat = st.slider("How Many Nurses are Available for Treatment?", 1, 10, step=1, value=4)

        else:
            nurses = st.slider("How Many Rooms/Nurses Are Available?", 1, 10, step=1, value=7)

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

            consult_time = st.slider("How long (in minutes) does a consultation take on average?",
                                        5, 120, step=5, value=50)

            consult_time_sd = st.slider("How much (in minutes) does the time for a consultation usually vary by?",
                                        5, 30, step=5, value=10)


        args = Scenario(
                    random_number_set=seed,
                    n_exam=nurses_advice,
                    n_cubicles_1=nurses_treat,
                    override_arrival_rate=True,
                    manual_arrival_rate=60/(mean_arrivals_per_day/24),
                    model="simple_with_branch",
                    trauma_treat_mean=consult_time,
                    trauma_treat_var=consult_time_sd
                    )
    with col2:
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
                            # Examination
                            {'event': 'examination_wait_begins', 'x':  150, 'y': 200, 'label': "Waiting for Examination"  },
                            {'event': 'examination_begins', 'x':  250, 'y': 100, 'resource':'n_exam', 'label': "Being Examined" },

                            # Treatment (optional step)                
                            {'event': 'treatment_wait_begins', 'x':  450, 'y': 200, 'label': "Waiting for Treatment"  },
                            {'event': 'treatment_begins', 'x':  550, 'y': 100, 'resource':'n_cubicles_1', 'label': "Being Treated" },
                        
                        ])
            animation_dfs_log = reshape_for_animations(
                        full_event_log=full_event_log[
                            (full_event_log['rep']==1) &
                            ((full_event_log['event_type']=='queue') | (full_event_log['event_type']=='resource_use')  | (full_event_log['event_type']=='arrival_departure'))
                        ],
                        every_x_minutes=5
                    )
    if button_run_pressed:
        st.subheader("Animated Model Output")
        with st.spinner('Generating the animated patient log...'):
            st.plotly_chart(animate_activity_log(
                                animation_dfs_log['full_patient_df'],
                                event_position_df = event_position_df,
                                scenario=args,
                                include_play_button=True,
                                display_stage_labels=False,
                                return_df_only=False,
                                plotly_height=600,
                                plotly_width=1000,
                                override_x_max=700,
                                override_y_max=675,
                                wrap_queues_at=10,
                                time_display_units="dhm",
                                add_background_image="https://raw.githubusercontent.com/Bergam0t/Teaching_DES_Concepts_Streamlit/main/resources/Branched%20Model%20Background%20Image%20-%20Horizontal%20Layout.drawio.png",
                        ), use_container_width=False)

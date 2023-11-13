'''
A Streamlit application based on Monks and 

Allows users to interact with an increasingly more complex treatment simulation 
'''
import streamlit as st
import asyncio
from helper_functions import read_file_contents, add_logo, mermaid
from model_classes import *
# from st_pages import show_pages_from_config, add_page_title

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

        with col2:
            # st.markdown("Placeholder")
            # args = Scenario(
            #             random_number_set=seed,
            #             n_cubicles_1=nurses,
            #             override_arrival_lambda=True,
            #             manual_arrival_lambda=60/(mean_arrivals_per_day/24),
            #             model="simplest",
            #             trauma_treat_mean=consult_time,
            #             trauma_treat_var=consult_time_sd
            #             )

            # n_reps = 8

            # # A user must press a streamlit button to run the model
            button_run_pressed = st.button("Run simulation")
            
            
            
            # if button_run_pressed:
                
            #     # add a spinner and then display success box
            #     with st.spinner('Simulating the minor injuries unit...'):
                    #   await asyncio.sleep(0.1)
            #         # run multiple replications of experment
            #         detailed_outputs = multiple_replications(
            #             args,
            #             n_reps=n_reps,
            #             rc_period=30*60*24,
            #             return_detailed_logs=True
            #         )

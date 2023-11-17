'''
A Streamlit application based on Monks and 

Allows users to interact with an increasingly more complex treatment simulation 
'''
import asyncio
import gc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from output_animation_functions import reshape_for_animations,animate_activity_log
from helper_functions import add_logo, mermaid
from model_classes import Scenario, multiple_replications

st.set_page_config(
     page_title="Adding an Optional Step",
     layout="wide",
     initial_sidebar_state="expanded",
 )

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
    """
    )

with tab3:

    col1, col2 = st.columns([1,1])

    with col1:
        
        nurses_advice = st.slider("How Many Nurses are Available for Examination?", 1, 10, step=1, value=3)

        consult_time_exam = st.slider("How long (in minutes) does an examination take on average?",
                                        5, 120, step=5, value=20)

        consult_time_sd_exam = st.slider("How much (in minutes) does the time for an examination usually vary by?",
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
                                    1, 40,
                                    step=1, value=15)

        
            mean_arrivals_per_day = st.slider("How many patients should arrive per day on average?",
                                            10, 300,
                                            step=5, value=140)    
        


    with col2:

        treat_p = st.slider("Probability that a patient will need treatment", 0.0, 1.0, step=0.01, value=0.7)

        nurses_treat = st.slider("How Many Doctors are Available for Treatment?", 1, 10, step=1, value=4)


        consult_time_treat = st.slider("How long (in minutes) does treatment take on average?",
                                        5, 120, step=5, value=50)

        consult_time_sd_treat = st.slider("How much (in minutes) does the time for treatment usually vary by?",
                                        5, 30, step=5, value=30)

        

    # A user must press a streamlit button to run the model
    button_run_pressed = st.button("Run simulation")
    
    args = Scenario(
            random_number_set=seed,
            n_exam=nurses_advice,
            n_cubicles_1=nurses_treat,
            override_arrival_rate=True,
            manual_arrival_rate=60/(mean_arrivals_per_day/24),
            model="simple_with_branch",
            exam_mean=consult_time_exam,
            exam_var=consult_time_sd_exam,
            non_trauma_treat_mean=consult_time_treat,
            non_trauma_treat_var=consult_time_sd_treat,
            non_trauma_treat_p=treat_p
            )
    
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

    if button_run_pressed:
        tab1, tab2, tab3 = st.tabs(
                ["Animated Log", "Simple Graphs", "Advanced Graphs"]
            )  
        with tab1:
            st.subheader("Animated Model Output")
            
            event_position_df = pd.DataFrame([
                            {'event': 'arrival', 'x':  50, 'y': 300, 'label': "Arrival" },
                            # Examination
                            {'event': 'examination_wait_begins', 'x':  150, 'y': 200, 'label': "Waiting for Examination"  },
                            {'event': 'examination_begins', 'x':  250, 'y': 100, 'resource':'n_exam', 'label': "Being Examined" },

                            # Treatment (optional step)                
                            {'event': 'treatment_wait_begins', 'x':  450, 'y': 200, 'label': "Waiting for Treatment"  },
                            {'event': 'treatment_begins', 'x':  550, 'y': 100, 'resource':'n_cubicles_1', 'label': "Being Treated" },
                        
                        ])

            with st.spinner('Generating the animated patient log...'):
                animation_dfs_log = reshape_for_animations(
                        full_event_log=full_event_log[
                            (full_event_log['rep']==1) &
                            ((full_event_log['event_type']=='queue') | (full_event_log['event_type']=='resource_use')  | (full_event_log['event_type']=='arrival_departure')) &
                            # Limit to first 5 days
                            (full_event_log['time'] <= 60*24*5)
                        ],
                        every_x_minutes=5
                    )['full_patient_df']

                st.plotly_chart(animate_activity_log(
                                    full_patient_df=animation_dfs_log[animation_dfs_log["minute"]<=60*24*5],
                                    event_position_df = event_position_df,
                                    scenario=args,
                                    include_play_button=True,
                                    display_stage_labels=False,
                                    return_df_only=False,
                                    plotly_height=600,
                                    plotly_width=1000,
                                    override_x_max=500,
                                    override_y_max=400,
                                    wrap_queues_at=10,
                                    time_display_units="dhm",
                                    add_background_image="https://raw.githubusercontent.com/Bergam0t/Teaching_DES_Concepts_Streamlit/main/resources/Branched%20Model%20Background%20Image%20-%20Horizontal%20Layout.drawio.png",
                            ), use_container_width=False)
        with tab2:
            in_range_util = sum((results.mean().filter(like="util")<0.85) & (results.mean().filter(like="util") > 0.65))
            in_range_wait = sum((results.mean().filter(regex="01a|02a")<120))            
            in_range_wait_perc = sum((results.mean().filter(like="01c")>0.85))        

            col_res_a, col_res_b = st.columns([1,1])

            with col_res_a:
                st.metric(label=":bed: **Utilisation Metrics in Ideal Range**", value="{} of {}".format(in_range_util, len(results.mean().filter(like="util"))))

                #util_fig_simple = px.bar(results.mean().filter(like="util"), opacity=0.5)
                st.markdown(
                    """
                    The emergency department wants to aim for an average of 65% to 85% utilisation across all resources in the emergency department. 
                    The green box shows this ideal range. If the bars overlap with the green box, utilisation is ideal. 
                    If utilisation is below this, you might want to **reduce** the number of those resources available. 
                    If utilisation is above this point, you may want to **increase** the number of that type of resource available.
                    """
                )
                util_fig_simple = go.Figure()
                # Add optimum range
                util_fig_simple.add_hrect(y0=0.65, y1=0.85,
                                          fillcolor="#5DFDA0", opacity=0.25,  line_width=0)
                # Add extreme range (above)
                util_fig_simple.add_hrect(y0=0.85, y1=1,
                                          fillcolor="#D45E5E", opacity=0.25, line_width=0)
                # Add suboptimum range (below)
                util_fig_simple.add_hrect(y0=0.4, y1=0.65,
                                          fillcolor="#FDD049", opacity=0.25, line_width=0)
                # Add extreme range (below)
                util_fig_simple.add_hrect(y0=0, y1=0.4,
                                          fillcolor="#D45E5E", opacity=0.25, line_width=0)

                util_fig_simple.add_bar(x=results.mean().filter(like="util").index.tolist(),
                                        y=results.mean().filter(like="util").tolist())

                util_fig_simple.update_layout(yaxis_tickformat = '.3%')
                util_fig_simple.update_yaxes(title_text='Resource Utilisation (%)',
                                             range=[-0.05, 1.1])
                # util_fig_simple.data = util_fig_simple.data[::-1]
                util_fig_simple.update_xaxes(labelalias={
                    "01b_treatment_util": "Treatment Bays", 
                }, tickangle=0)
                
                util_fig_simple.update_layout(margin=dict(l=0, r=0, t=0, b=0))

                st.plotly_chart(
                    util_fig_simple,
                    use_container_width=True,
                    config = {'displayModeBar': False}
                )

            
            with col_res_b:
                #util_fig_simple = px.bar(results.mean().filter(like="wait"), opacity=0.5)
                st.metric(label=":clock2: **Wait Metrics in Ideal Range**", value="{} of {}".format(in_range_wait, len(results.mean().filter(like="wait"))))

                st.markdown(
                    """
                    The emergency department wants to ensure people wait no longer than 2 hours (120 minutes) to be seen.
                    This needs to be balanced with the utilisation graphs on the left.
                    The green box shows waits of less than two hours. If the bars fall within this range, the number of resources does not need to be changed.
                    """
                )

                wait_fig_simple = go.Figure()
                wait_fig_simple.add_hrect(y0=0, y1=60*2, fillcolor="#5DFDA0", 
                                          opacity=0.3, line_width=0)
                
                wait_fig_simple.add_bar(x=results.mean().filter(regex="01a|02a").index.tolist(),
                                        y=results.mean().filter(regex="01a|02a").tolist())

                wait_fig_simple.update_xaxes(labelalias={
                    "01a_treatment_wait": "Treatment"
                }, tickangle=0)
                # wait_fig_simple.data = wait_fig_simple.data[::-1]
                wait_fig_simple.update_yaxes(title_text='Wait for Treatment Stage (Minutes)')

                wait_fig_simple.update_layout(margin=dict(l=0, r=0, t=0, b=0))

                st.plotly_chart(
                    wait_fig_simple,
                    use_container_width=True,
                    config = {'displayModeBar': False}
                )

            col_res_c, col_res_d = st.columns(2)

            with col_res_c:
                #util_fig_simple = px.bar(results.mean().filter(like="wait"), opacity=0.5)
                st.metric(label=":clock2: **Wait Target Met**", value="{} of {}".format(in_range_wait_perc, len(results.mean().filter(like="wait"))))

                st.markdown(
                    """
                    The emergency department wants to ensure people wait no longer than 2 hours (120 minutes) to be seen.
                    This needs to be balanced with the utilisation graphs on the left.
                    The green box shows waits of less than two hours. If the bars fall within this range, the number of resources does not need to be changed.
                    """
                )

                wait_target_simple = go.Figure()
                wait_target_simple.add_hrect(y0=0.85, y1=1, fillcolor="#5DFDA0", 
                                          opacity=0.3, line_width=0)
                
                wait_target_simple.add_bar(x=results.median().filter(like="01c").index.tolist(),
                                        y=results.median().filter(like="01c").tolist())

                wait_fig_simple.update_xaxes(labelalias={
                    "01c_treatment_wait_target_met": "Treatment Wait - Target Met" 
                }, tickangle=0)
                # wait_fig_simple.data = wait_fig_simple.data[::-1]
                wait_target_simple.update_yaxes(title_text='Average % of patients where 2 hour wait target met')

                wait_target_simple.update_layout(margin=dict(l=0, r=0, t=0, b=0))

                st.plotly_chart(
                    wait_target_simple,
                    use_container_width=True,
                    config = {'displayModeBar': False}
                )


                # st.write(results)
        with tab3:

            st.markdown(
            """
            We can use **box plots** to help us understand the variation in each result during a model run. 
            
            Because of the variation in the patterns of arrivals, as well as the variation in the length of consultations, we may find that sometimes model runs fall within our desired ranges but other times, despite the parameters being the same, they don't. 

            This gives us a better idea of how likely a redesigned system is to meet the targets.
            """
            )

            st.markdown("""
                        ### Utilisation
                        """)
            util_box = px.box(
                    results.reset_index().melt(id_vars=["rep"]).set_index('variable').filter(like="util", axis=0).reset_index(), 
                    y="variable", 
                    x="value",
                    points="all",
                    range_x=[0, 1.1],
                    height=200)
            
            util_box.update_layout(yaxis_title="", xaxis_title="Average Utilisation in Model Run")

            util_box.add_vrect(x0=0.65, x1=0.85,
                                          fillcolor="#5DFDA0", opacity=0.25,  line_width=0)
            # Add extreme range (above)
            util_box.add_vrect(x0=0.85, x1=1,
                                        fillcolor="#D45E5E", opacity=0.25, line_width=0)
            # Add suboptimum range (below)
            util_box.add_vrect(x0=0.4, x1=0.65,
                                        fillcolor="#FDD049", opacity=0.25, line_width=0)
            # Add extreme range (below)
            util_box.add_vrect(x0=0, x1=0.4,
                                        fillcolor="#D45E5E", opacity=0.25, line_width=0)

            util_box.update_yaxes(labelalias={
                "01b_treatment_util": "Treatment<br>Bays"
            }, tickangle=0)



            st.plotly_chart(util_box,
                    use_container_width=True
                )
                

            st.markdown("""
                        ### Waits
                        """)
            wait_box = px.box(
                    results.reset_index().melt(id_vars=["rep"]).set_index('variable').filter(regex="01a|02a", axis=0).reset_index(), 
                    y="variable", 
                    x="value",
                    points="all",
                    height=200,
                    range_x=[0, results.reset_index().melt(id_vars=["rep"]).set_index('variable').filter(regex="01a|02a", axis=0).reset_index().max().value]
                    )
            wait_box.update_layout(yaxis_title="", xaxis_title="Average Wait in Model Run")

            wait_box.update_yaxes(labelalias={
                    "01a_treatment_wait": "Treatment Wait"
                }, tickangle=0)

            wait_box.add_vrect(x0=0, x1=60*2, fillcolor="#5DFDA0", 
                                          opacity=0.3, line_width=0)

            st.plotly_chart(wait_box,
                    use_container_width=True
                )

            st.markdown("""
                        ### Wait Targets
                        This is the percentage of clients who met the 2 hour wait target.
                        """)

            wait_target_box = px.box(
                    results.reset_index().melt(id_vars=["rep"]).set_index('variable').filter(like="1c", axis=0).reset_index(), 
                    y="variable", 
                    x="value",
                    points="all",
                    height=200,
                    range_x=[0, 1.1]
                    )
            
            wait_target_box.update_layout(yaxis_title="", xaxis_title="% of clients meeting waiting time target")

            wait_target_box.update_yaxes(labelalias={
                "01c_treatment_wait_target_met": "Waiting Time Target<br>(% met)"
            }, tickangle=0)


            st.plotly_chart(wait_target_box,
                    use_container_width=True
                )
 
            st.markdown("""
                        ### Throughput
                        This is the percentage of clients who entered the system who had left by the time the model stopped running.
                        Higher values are better - low values suggest a big backlog of people getting stuck in the system for a long time.
                        """)
            
            results['perc_throughput'] = results['09_throughput']/results['00_arrivals']
            throughput_box = px.box(
                    results.reset_index().melt(id_vars=["rep"]).set_index('variable').filter(like="perc_throughput", axis=0).reset_index(), 
                    y="variable", 
                    x="value",
                    points="all",
                    height=200,
                    range_x=[0, 1.1]
                    )
            
            throughput_box.update_layout(yaxis_title="", xaxis_title="Throughput in Model Run")

            throughput_box.update_yaxes(labelalias={
                "09_throughput": "Throughput"
            }, tickangle=0)


            st.plotly_chart(throughput_box,
                    use_container_width=True
                )

gc.collect()
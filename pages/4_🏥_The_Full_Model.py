'''
A Streamlit application based on Monks and 

Allows users to interact with an increasingly more complex treatment simulation 
'''
import gc
import asyncio
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from helper_functions import add_logo, mermaid
from model_classes import Scenario, multiple_replications
from output_animation_functions import reshape_for_animations, animate_activity_log

st.set_page_config(
     page_title="The Full Model",
     layout="wide",
     initial_sidebar_state="expanded",
 )

# Initialise session state
if 'session_results' not in st.session_state:
    st.session_state['session_results'] = []

add_logo()

with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

## We add in a title for our web app's page
st.title("Discrete Event Simulation Playground")
st.subheader("How can we optimise the full system?")

tab1, tab2, tab3, tab4 = st.tabs(["Introduction", "Exercises", "Playground", "Compare Scenario Outputs"])
with tab1:
    st.markdown("""
                So now we have explored every component of the model:
                - Generating arrivals
                - Generating and using resources
                - Sending people down different paths 
                
                So now let's create a version of the model that uses all of these aspects. 

                For now, we won't consider nurses separately - we will assume that each nurse on shift has one room that is theirs to always use.
                """
                )
    
    mermaid(height=600, code=
    """
    %%{ init: { 'flowchart': { 'curve': 'step' } } }%%
    %%{ init: {  'theme': 'base', 'themeVariables': {'lineColor': '#b4b4b4'} } }%%
    flowchart LR
        A[Arrival] --> BX[Triage]
        BX -.-> T([Triage Bay\n<b>RESOURCE</b>])
        T -.-> BX

        BX --> BY{Trauma or non-trauma}
        BY ----> B1{Trauma Pathway} 
        BY ----> B2{Non-Trauma Pathway}
        
        B1 --> C[Stabilisation]
        C --> E[Treatment]
      
        B2 --> D[Registration]
        D --> G[Examination]

        G --> H[Treat?]
        H ----> F 

        H --> I[Non-Trauma Treatment]
        I --> F 

        C -.-> Z([Trauma Room\n<b>RESOURCE</b>])
        Z -.-> C

        E -.-> Y([Cubicle - 1\n<b>RESOURCE</b>])
        Y -.-> E

        D -.-> X([Clerks\n<b>RESOURCE</b>])
        X -.-> D

        G -.-> W([Exam Room\n<b>RESOURCE</b>])
        W -.-> G

        I -.-> V([Cubicle - 2\n<b>RESOURCE</b>])
        V -.-> I

        E ----> F[Discharge]

        classDef ZZ1 fill:#8B5E0F,font-family:lexend, color:#FFF
        classDef ZZ2 fill:#5DFDA0,font-family:lexend
        classDef ZZ2a fill:#02CD55,font-family:lexend, color:#FFF
        classDef ZZ3 fill: #D45E5E,font-family:lexend
        classDef ZZ3a fill: #932727,font-family:lexend, color:#FFF
        classDef ZZ4 fill: #611D67,font-family:lexend, color:#FFF
        classDef ZZ5 fill:#47D7FF,font-family:lexend
        classDef ZZ5a fill:#00AADA,font-family:lexend

        class A ZZ1
        class C,E ZZ2
        class D,G ZZ3
        class X,W ZZ3a
        class Z,Y ZZ2a
        class I,V ZZ4
        class BX ZZ5
        class T ZZ5a
        ;
    """
)
    
with tab2:
    st.header("Things to Try")

    st.markdown(
        """
        - Run the animated model output. Are the queues consistent throughout the day?
        
        - Try changing the number of resources you have available so that all resources in your ED have an average utilisation of between 65% and 85% while the wait for treatment is under 4 hours. Is it possible to balance these requirements?

        - Imagine you have a maximum of 15 rooms and cubicles. What is the best configuration of rooms you can find to keep the average wait times as low as possible across both trauma and non-trauma pathways?
        """
    )

with tab3:
    
    # n_triage: int
    #         The number of triage cubicles

    # n_reg: int
    #     The number of registration clerks

    # n_exam: int
    #     The number of examination rooms

    # n_trauma: int
    #     The number of trauma bays for stablisation

    # n_cubicles_1: int
    #     The number of non-trauma treatment cubicles

    # n_cubicles_2: int
    #     The number of trauma treatment cubicles

    # non_trauma_treat_p: float
    #     Probability non trauma patient requires treatment

    # prob_trauma: float
    #     probability that a new arrival is a trauma patient.
    

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.subheader("Triage")
        n_triage = st.slider("🧑‍⚕️ Number of Triage Cubicles", 1, 10, step=1, value=4)
        prob_trauma = st.slider("🚑 Probability that a new arrival is a trauma patient", 0.0, 1.0, step=0.01, value=0.3)

    with col2:
        st.subheader("Trauma Pathway")
        n_trauma = st.slider("🧑‍⚕️ Number of Trauma Bays for Stabilisation", 1, 10, step=1, value=6)
        n_cubicles_2 = st.slider("🧑‍⚕️ Number of Treatment Cubicles for Trauma", 1, 10, step=1, value=6)

    with col3:
        st.subheader("Non-Trauma Pathway")
        n_reg = st.slider("🧑‍⚕️ Number of Registration Cubicles", 1, 10, step=1, value=3)
        n_exam = st.slider("🧑‍⚕️ Number of Examination Rooms for non-trauma patients", 1, 10, step=1, value=3)

    with col4: 
        st.subheader("Non-trauma Treatment")
        n_cubicles_1 = st.slider("🧑‍⚕️ Number of Treatment Cubicles for Non-Trauma", 1, 10, step=1, value=2)
        non_trauma_treat_p = st.slider("🤕 Probability that a non-trauma patient will need treatment", 0.0, 1.0, step=0.01, value=0.7)


    col5, col6 = st.columns(2)
    with col5:
        st.write("Total rooms in use is {}".format(n_cubicles_1+n_cubicles_2+n_exam+n_trauma+n_triage+n_reg))
    with col6:
        with st.expander("Advanced Parameters"):
            seed = st.number_input("🎲 Set a random number for the computer to start from",
                            1, 10000000,
                            step=1, value=42)

            n_reps = st.slider("🔁 How many times should the simulation run? WARNING: Fast/modern computer required to take this above 5 replications.",
                            1, 10,
                            step=1, value=3)
            
            run_time_days = st.slider("🗓️ How many days should we run the simulation for each time?",
                        1, 60,
                        step=1, value=10)

    args = Scenario(
        random_number_set=seed,
                 n_triage=n_triage,
                 n_reg=n_reg,
                 n_exam=n_exam,
                 n_trauma=n_trauma,
                 n_cubicles_1=n_cubicles_1,
                 n_cubicles_2=n_cubicles_2,
                 non_trauma_treat_p=non_trauma_treat_p,
                 prob_trauma=prob_trauma)
    
    # A user must press a streamlit button to run the model
    button_run_pressed = st.button("Run simulation")
    
    
    if button_run_pressed:

        # add a spinner and then display success box
        with st.spinner('Simulating the minor injuries unit...'):
            await asyncio.sleep(0.1)

            my_bar = st.progress(0, text="Simulating the minor injuries unit...")

            # run multiple replications of experment
            detailed_outputs = multiple_replications(
                args,
                n_reps=n_reps,
                rc_period=run_time_days*60*24,
                return_detailed_logs=True
            )

            my_bar.progress(40, text="Collating Simulation Outputs...")


            results = pd.concat([detailed_outputs[i]['results']['summary_df'].assign(rep= i+1)
                                        for i in range(n_reps)]).set_index('rep')
            
            full_event_log = pd.concat([detailed_outputs[i]['results']['full_event_log'].assign(rep= i+1)
                                        for i in range(n_reps)])
            
            my_bar.progress(60, text="Logging Results...")

            # print(len(st.session_state['session_results']))
            # results_for_state = pd.DataFrame(results.median()).T.drop(['Rep'], axis=1)
            results_for_state = results
            original_cols = results_for_state.columns.values
            results_for_state['Triage\nCubicles'] = args.n_triage
            results_for_state['Registration\nClerks'] = args.n_reg
            results_for_state['Examination\nRooms'] = args.n_exam
            results_for_state['Non-Trauma\nTreatment Cubicles'] = args.n_cubicles_1
            results_for_state['Trauma\nStabilisation Bays'] = args.n_trauma
            results_for_state['Trauma\nTreatment Cubicles'] = args.n_cubicles_2
            results_for_state['Probability patient\nis a trauma patient'] = args.prob_trauma
            results_for_state['Probability non-trauma patients\nrequire treatment'] = args.non_trauma_treat_p
            results_for_state['Model Run'] = len(st.session_state['session_results']) + 1
            results_for_state['Random Seed'] = seed

            # Reorder columns
            column_order = ['Model Run', 'Triage\nCubicles', 'Registration\nClerks', 'Examination\nRooms',
                            'Non-Trauma\nTreatment Cubicles', 'Trauma\nStabilisation Bays', 
                            'Trauma\nTreatment Cubicles', 'Probability patient\nis a trauma patient',
                            'Probability non-trauma patients\nrequire treatment', 'Random Seed'
                            ] + list(original_cols)

            results_for_state = results_for_state[column_order]

            current_state = st.session_state['session_results']

            current_state.append(results_for_state)
            del results_for_state

            st.session_state['session_results'] = current_state

            # print(len(st.session_state['session_results']))

            # UTILISATION AUDIT - BRING BACK WHEN NEEDED
            # full_utilisation_audit = pd.concat([detailed_outputs[i]['results']['utilisation_audit'].assign(Rep= i+1)
            #                         for i in range(n_reps)])
            
            # animation_dfs_queue = reshape_for_animations(
            #     full_event_log[
            #         (full_event_log['rep']==1) &
            #         ((full_event_log['event_type']=='queue') | (full_event_log['event_type']=='arrival_departure'))
            #     ]
            # )

            my_bar.progress(80, text="Creating Animations...")

            animation_dfs_log = reshape_for_animations(
                full_event_log=full_event_log[
                    (full_event_log['rep']==1) &
                    ((full_event_log['event_type']=='queue') | (full_event_log['event_type']=='resource_use')  | (full_event_log['event_type']=='arrival_departure')) &
                     # Limit to first 5 days
                    (full_event_log['time'] <= 60*24*5)
                ],
                every_x_minutes=5
            )['full_patient_df']

        del full_event_log
        gc.collect()
        my_bar.progress(100, text="Simulation Complete!")
        # st.write(results.reset_index())

        # st.write(pd.wide_to_long(results, stubnames=['util', 'wait'],
        #                          i="rep", j="metric_type",
        #                          sep='_', suffix='.*'))

        # st.write(results.reset_index().melt(id_vars="rep").set_index('variable').filter(like="util", axis=0))

        # Add in a box plot showing utilisation

        tab_playground_results_1, tab_playground_results_2, tab_playground_results_3, tab_playground_results_4  = st.tabs([
            'Utilisation and Wait Metrics',
            'Animated Model',
            'Advanced Utilisation and Wait Metrics',
            'Utilisation over Time'
            ])

        # st.subheader("Look at Average Results Across Replications")

        with tab_playground_results_2:
            
            event_position_df = pd.DataFrame([
                # {'event': 'arrival', 'x':  10, 'y': 250, 'label': "Arrival" },
                
                # Triage - minor and trauma                
                {'event': 'triage_wait_begins', 
                 'x':  160, 'y': 400, 'label': "Waiting for<br>Triage"  },
                {'event': 'triage_begins', 
                 'x':  160, 'y': 315, 'resource':'n_triage', 'label': "Being Triaged" },
            
                # Minors (non-trauma) pathway 
                {'event': 'MINORS_registration_wait_begins', 
                 'x':  300, 'y': 145, 'label': "Waiting for<br>Registration"  },
                {'event': 'MINORS_registration_begins', 
                 'x':  300, 'y': 85, 'resource':'n_reg', 'label':'Being<br>Registered'  },

                {'event': 'MINORS_examination_wait_begins', 
                 'x':  465, 'y': 145, 'label': "Waiting for<br>Examination"  },
                {'event': 'MINORS_examination_begins', 
                 'x':  465, 'y': 85, 'resource':'n_exam', 'label': "Being<br>Examined" },

                {'event': 'MINORS_treatment_wait_begins', 
                 'x':  630, 'y': 145, 'label': "Waiting for<br>Treatment"  },
                {'event': 'MINORS_treatment_begins', 
                 'x':  630, 'y': 85, 'resource':'n_cubicles_1', 'label': "Being<br>Treated" },

                # Trauma pathway
                {'event': 'TRAUMA_stabilisation_wait_begins', 
                 'x': 300, 'y': 560, 'label': "Waiting for<br>Stabilisation" },
                {'event': 'TRAUMA_stabilisation_begins', 
                 'x': 300, 'y': 500, 'resource':'n_trauma', 'label': "Being<br>Stabilised" },

                {'event': 'TRAUMA_treatment_wait_begins', 
                 'x': 630, 'y': 560, 'label': "Waiting for<br>Treatment" },
                {'event': 'TRAUMA_treatment_begins', 
                 'x': 630, 'y': 500, 'resource':'n_cubicles_2', 'label': "Being<br>Treated" }
            ])

            animated_plot = animate_activity_log(
                    full_patient_df=animation_dfs_log[animation_dfs_log["minute"]<=60*24*5],
                    event_position_df = event_position_df,
                    scenario=args,
                    include_play_button=True,
                    return_df_only=False,
                    plotly_height=900,
                    plotly_width=1600,
                    override_x_max=700,
                    override_y_max=675,
                    icon_and_text_size=24,
                    display_stage_labels=False,
                    wrap_queues_at=10,
                    time_display_units="dhm",
                    # show_animated_clock=True,
                    # animated_clock_coordinates = [100, 50],
                    add_background_image="https://raw.githubusercontent.com/Bergam0t/Teaching_DES_Concepts_Streamlit/main/resources/Full%20Model%20Background%20Image%20-%20Horizontal%20Layout.drawio.png",
            )

            st.plotly_chart(animated_plot,
                            use_container_width=False)

            # st.markdown(
            #     f'<a href="data:text/html;base64,{base64.b64encode(animated_plot.to_html(full_html=False, include_plotlyjs="cdn").encode()).decode()}" download="plot.html">Download Plot</a>',
            #     unsafe_allow_html=True
            # )

            st.download_button(
                label="Download Plot as HTML",
                data=animated_plot.to_html(full_html=False, include_plotlyjs="cdn"),
                file_name="plot.html",
                mime="text/html"
            )


            # Uncomment if debugging animated event log
            # st.write(
            #     animate_activity_log(
            #         animation_dfs_log['full_patient_df'],
            #         event_position_df = event_position_df,
            #         scenario=args,
            #         include_play_button=True,
            #         return_df_only=True
            # ).sort_values(['patient', 'minute'])
            # )

            # st.write(
            #          animation_dfs_log['full_patient_df'].sort_values(['patient', 'minute'])
            # )

        # st.write(animation_dfs_log['full_patient_df'].sort_values('minute'))
        # st.write(animation_dfs_log['full_patient_df'].sort_values(['minute', 'event'])[['minute', 'event', 'patient', 'resource_id', 'resource_users', 'request']]
                #  )

        with tab_playground_results_1:

            in_range_util = sum((results.mean().filter(like="util")<0.85) & (results.mean().filter(like="util") > 0.65))
            in_range_wait = sum((results.mean().filter(like="wait")<120))
                                

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

                util_fig_simple.update_layout(yaxis_tickformat = '.0%')
                util_fig_simple.update_yaxes(title_text='Resource Utilisation (%)',
                                             range=[-0.05, 1.1])
                # util_fig_simple.data = util_fig_simple.data[::-1]
                util_fig_simple.update_xaxes(labelalias={
                    "01b_triage_util": "Triage<br>Bays", 
                    "02b_registration_util": "Registration<br>Cubicles",
                    "03b_examination_util": "Examination<br>Bays",
                    "04b_treatment_util(non_trauma)": "Treatment<br>Bays<br>(non-trauma)",
                    "06b_trauma_util": "Stabilisation<br>Bays",
                    "07b_treatment_util(trauma)": "Treatment<br>Bays<br>(trauma)"
                }, tickangle=0)
                st.plotly_chart(
                    util_fig_simple,
                    use_container_width=True
                )

            
            with col_res_b:
                #util_fig_simple = px.bar(results.mean().filter(like="wait"), opacity=0.5)
                st.metric(label=":clock2: **Wait Metrics in Ideal Range**", value="{} of {}".format(in_range_wait, len(results.mean().filter(like="wait"))))

                st.markdown(
                    """
                    The emergency department wants to ensure people wait no longer than 2 hours (120 minutes) at any point in the process.
                    This needs to be balanced with the utilisation graphs on the left.
                    The green box shows waits of less than two hours. If the bars fall within this range, the number of resources does not need to be changed.
                    """
                )

                wait_fig_simple = go.Figure()
                wait_fig_simple.add_hrect(y0=0, y1=60*2, fillcolor="#5DFDA0", 
                                          opacity=0.3, line_width=0)
                
                wait_fig_simple.add_bar(x=results.mean().filter(like="wait").index.tolist(),
                                        y=results.mean().filter(like="wait").tolist())

                wait_fig_simple.update_xaxes(labelalias={
                    "01a_triage_wait": "Triage", 
                    "02a_registration_wait": "Registration",
                    "03a_examination_wait": "Examination",
                    "04a_treatment_wait(non_trauma)": "Treatment<br>(non-trauma)",
                    "06a_trauma_wait": "Stabilisation",
                    "07a_treatment_wait(trauma)": "Treatment<br>(trauma)"
                }, tickangle=0)
                # wait_fig_simple.data = wait_fig_simple.data[::-1]
                wait_fig_simple.update_yaxes(title_text='Wait for Treatment Stage (Minutes)')

                st.plotly_chart(
                    wait_fig_simple,
                    use_container_width=True
                )


        with tab_playground_results_3:

            st.markdown("""
                        We can use box plots to explore the effect of the random variation within each model run.
                        This can give us a better idea of how robust the system is. 
                        """)

            col_res_1, col_res_2 = st.columns(2)

            with col_res_1:
                st.subheader("Average Utilisation")

                utilisation_boxplot = px.box(
                    results.reset_index().melt(id_vars="rep").set_index('variable').filter(like="util", axis=0).reset_index(), 
                    y="variable", 
                    x="value",
                    points="all",
                    range_x=[0, 1])
                
                utilisation_boxplot.add_vrect(x0=0.65, x1=0.85,
                                          fillcolor="#5DFDA0", opacity=0.25,  line_width=0)
                # Add extreme range (above)
                utilisation_boxplot.add_vrect(x0=0.85, x1=1,
                                          fillcolor="#D45E5E", opacity=0.25, line_width=0)
                # Add suboptimum range (below)
                utilisation_boxplot.add_vrect(x0=0.4, x1=0.65,
                                          fillcolor="#FDD049", opacity=0.25, line_width=0)
                # Add extreme range (below)
                utilisation_boxplot.add_vrect(x0=0, x1=0.4,
                                          fillcolor="#D45E5E", opacity=0.25, line_width=0)

                utilisation_boxplot.update_yaxes(labelalias={
                    "01b_triage_util": "Triage<br>Bays", 
                    "02b_registration_util": "Registration<br>Cubicles",
                    "03b_examination_util": "Examination<br>Bays",
                    "04b_treatment_util(non_trauma)": "Treatment<br>Bays<br>(non-trauma)",
                    "06b_trauma_util": "Stabilisation<br>Bays",
                    "07b_treatment_util(trauma)": "Treatment<br>Bays<br>(trauma)"
                }, tickangle=0)

                utilisation_boxplot.update_layout(xaxis_tickformat = '.0%')
                

                st.plotly_chart(utilisation_boxplot,
                    use_container_width=True
                    )
                
                st.write(results.filter(like="util", axis=1).merge(results.filter(like="throughput", axis=1),left_index=True,right_index=True))
                
            with col_res_2:
                st.subheader("Average Waits")

                wait_boxplot = px.box(
                    results.reset_index().melt(id_vars="rep").set_index('variable').filter(like="wait", axis=0).reset_index(), 
                    y="variable", 
                    x="value",
                    points="all")

                wait_boxplot.update_yaxes(labelalias={
                    "01a_triage_wait": "Triage", 
                    "02a_registration_wait": "Registration",
                    "03a_examination_wait": "Examination",
                    "04a_treatment_wait(non_trauma)": "Treatment<br>(non-trauma)",
                    "06a_trauma_wait": "Stabilisation",
                    "07a_treatment_wait(trauma)": "Treatment<br>(trauma)"
                }, tickangle=0)

                wait_boxplot.add_vrect(x0=0, x1=60*2, fillcolor="#5DFDA0", 
                                          opacity=0.3, line_width=0)

                # Add in a box plot showing waits
                st.plotly_chart(wait_boxplot,
                    use_container_width=True
                    )

                st.write(results.filter(like="wait", axis=1)
                        .merge(results.filter(like="throughput", axis=1), 
                                left_index=True, right_index=True))


        

        with tab_playground_results_4:
            st.markdown("Placeholder")

#################################################
# Create area for exploring all session results
#################################################
with tab4:
    if len(st.session_state['session_results']) > 0:


        all_run_results = pd.concat(st.session_state['session_results'])

        st.subheader("Look at Average Results Across Replications")
        col_a, col_b = st.columns(2)
        
        with col_a:
            # st.write(all_run_results.drop(all_run_results.filter(regex='\d+').columns,axis=1).groupby('Model Run').median().T)
            st.write(all_run_results.groupby('Model Run').median().T)


        scenario_tab_1, scenario_tab_2, scenario_tab_3 = st.tabs([
            "Simple Metrics", 
            "Advanced Metrics",
            "Detailed Breakdown"])
        

        with scenario_tab_1:

#             st.write(
# all_run_results.groupby('Model Run').median().T.reset_index(drop=False).melt(id_vars="index", var_name="model_run"),                    x="variable", 
#             )
            col_x, col_y = st.columns(2)

            with col_x:
                st.subheader("Utilisation")

                all_run_util_bar = px.bar(
                        all_run_results.groupby('Model Run').median().T.filter(like="util", axis=0).reset_index(drop=False).melt(id_vars="index", var_name="model_run"),              
                        x="value",
                        y="index",
                        barmode='group',
                        color="model_run",
                        range_x=[0, 1])
                
                all_run_util_bar.add_vrect(x0=0.65, x1=0.85,
                                          fillcolor="#5DFDA0", opacity=0.25,  line_width=0)
                # Add extreme range (above)
                all_run_util_bar.add_vrect(x0=0.85, x1=1,
                                          fillcolor="#D45E5E", opacity=0.25, line_width=0)
                # Add suboptimum range (below)
                all_run_util_bar.add_vrect(x0=0.4, x1=0.65,
                                          fillcolor="#FDD049", opacity=0.25, line_width=0)
                # Add extreme range (below)
                all_run_util_bar.add_vrect(x0=0, x1=0.4,
                                          fillcolor="#D45E5E", opacity=0.25, line_width=0)

                all_run_util_bar.update_yaxes(labelalias={
                    "01b_triage_util": "Triage<br>Bays", 
                    "02b_registration_util": "Registration<br>Cubicles",
                    "03b_examination_util": "Examination<br>Bays",
                    "04b_treatment_util(non_trauma)": "Treatment<br>Bays<br>(non-trauma)",
                    "06b_trauma_util": "Stabilisation<br>Bays",
                    "07b_treatment_util(trauma)": "Treatment<br>Bays<br>(trauma)"
                }, tickangle=0)

                all_run_util_bar.update_layout(yaxis_tickformat = '.0%')

                st.plotly_chart(
                    all_run_util_bar,
                        use_container_width=True
                        )
                
            with col_y:
                st.subheader("Waits")

                all_run_wait_bar = px.bar(
                        all_run_results.groupby('Model Run').median().T.filter(like="wait", axis=0).reset_index(drop=False).melt(id_vars="index", var_name="model_run"),              
                        x="value",
                        y="index",
                        barmode='group',
                        color="model_run",
                        )
                
                all_run_wait_bar.update_yaxes(labelalias={
                    "01a_triage_wait": "Triage", 
                    "02a_registration_wait": "Registration",
                    "03a_examination_wait": "Examination",
                    "04a_treatment_wait(non_trauma)": "Treatment<br>(non-trauma)",
                    "06a_trauma_wait": "Stabilisation",
                    "07a_treatment_wait(trauma)": "Treatment<br>(trauma)"
                }, tickangle=0)

                all_run_wait_bar.add_vrect(x0=0, x1=60*2, fillcolor="#5DFDA0", 
                                          opacity=0.3, line_width=0)

                st.plotly_chart(all_run_wait_bar,
                        use_container_width=True
                        )
        
        # Repeat but with boxplots instead so variability within model runs can be
        # better explored
        with scenario_tab_2:

            col_res_1, col_res_2 = st.columns(2)

            

            with col_res_1:
                st.subheader("Utilisation")

                all_run_util_box = px.box(
                    all_run_results.reset_index().melt(id_vars=["Model Run", "rep"]).set_index('variable').filter(like="util", axis=0).reset_index(), 
                    y="variable", 
                    x="value",
                    color="Model Run",
                    points="all",
                    range_x=[0, 1])

                all_run_util_box.add_vrect(x0=0.65, x1=0.85,
                                          fillcolor="#5DFDA0", opacity=0.25,  line_width=0)
                # Add extreme range (above)
                all_run_util_box.add_vrect(x0=0.85, x1=1,
                                          fillcolor="#D45E5E", opacity=0.25, line_width=0)
                # Add suboptimum range (below)
                all_run_util_box.add_vrect(x0=0.4, x1=0.65,
                                          fillcolor="#FDD049", opacity=0.25, line_width=0)
                # Add extreme range (below)
                all_run_util_box.add_vrect(x0=0, x1=0.4,
                                          fillcolor="#D45E5E", opacity=0.25, line_width=0)

                all_run_util_box.update_yaxes(labelalias={
                    "01b_triage_util": "Triage<br>Bays", 
                    "02b_registration_util": "Registration<br>Cubicles",
                    "03b_examination_util": "Examination<br>Bays",
                    "04b_treatment_util(non_trauma)": "Treatment<br>Bays<br>(non-trauma)",
                    "06b_trauma_util": "Stabilisation<br>Bays",
                    "07b_treatment_util(trauma)": "Treatment<br>Bays<br>(trauma)"
                }, tickangle=0)

                all_run_util_box.update_layout(xaxis_tickformat = '.0%')

                st.plotly_chart(all_run_util_box,
                    use_container_width=True
                    )
                



                # st.write(all_run_results.filter(like="util", axis=1).merge(all_run_results.filter(like="throughput", axis=1),left_index=True,right_index=True))
                
            with col_res_2:
                st.subheader("Waits")

                all_run_wait_box = px.box(
                    all_run_results.reset_index().melt(id_vars=["Model Run", "rep"]).set_index('variable').filter(like="wait", axis=0).reset_index(), 
                #                 left_index=True, right_index=True), 
                    y="variable", 
                    x="value",
                    color="Model Run",
                    points="all", 
                    height=800)
                
                all_run_wait_box.update_yaxes(labelalias={
                    "01a_triage_wait": "Triage", 
                    "02a_registration_wait": "Registration",
                    "03a_examination_wait": "Examination",
                    "04a_treatment_wait(non_trauma)": "Treatment<br>(non-trauma)",
                    "06a_trauma_wait": "Stabilisation",
                    "07a_treatment_wait(trauma)": "Treatment<br>(trauma)"
                }, tickangle=0)

                all_run_wait_box.add_vrect(x0=0, x1=60*2, fillcolor="#5DFDA0", 
                                          opacity=0.3, line_width=0)
                # Add in a box plot showing waits
                st.plotly_chart(all_run_wait_box,
                    use_container_width=True
                    )

            col_res_3, col_res_4 = st.columns(2)

            with col_res_3:
                st.subheader("Throughput")
                st.markdown(
                    """
                    This is the percentage of clients who entered the system
                    who had left by the time the model stopped running.
                    Higher values are better - low values suggest a big backlog of people getting stuck in the system
                    for a long time.
                    """
                )
                all_run_results['perc_throughput'] = all_run_results['09_throughput']/all_run_results['00_arrivals']


                all_results_throughput_box = px.box(
                    all_run_results.reset_index().melt(id_vars=["Model Run", "rep"]).set_index('variable').filter(like="perc_throughput", axis=0).reset_index(),  
                    y="variable", 
                    x="value",
                    color="Model Run",
                    points="all",
                    height=800)
                
                all_results_throughput_box.update_layout(xaxis_tickformat = '.0%')

                # Add in a box plot showing waits
                st.plotly_chart(all_results_throughput_box,
                    use_container_width=True
                    )

                # st.write(all_run_results.filter(like="wait", axis=1)
                #             .merge(all_run_results.filter(like="throughput", axis=1), 
                #                 left_index=True, right_index=True))
        with scenario_tab_3:
            st.write(all_run_results)

            st.write(all_run_results.groupby('Model Run').median().T)
    else:
        st.markdown("No scenarios yet run. Go to the 'Playground' tab and click 'Run simulation'.")

gc.collect()
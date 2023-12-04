'''
A Streamlit application based on Monks and 

Allows users to interact with an increasingly more complex treatment simulation 
'''
import time
import asyncio
import datetime as dt
import gc
import numpy as np
import plotly.express as px
import pandas as pd
import streamlit as st

from helper_functions import add_logo, mermaid
from model_classes import Scenario, multiple_replications
from distribution_classes import Exponential

st.set_page_config(
    page_title="Simulating Arrivals",
    layout="wide",
    initial_sidebar_state="expanded",
)

add_logo()

# try:
#     running_on_st_community = st.secrets["IS_ST_COMMUNITY"]
# except FileNotFoundError:
#     running_on_st_community = False

with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# We add in a title for our web app's page
st.title("Discrete Event Simulation Playground")
st.subheader("Simulating Patients Arriving at the Centre")

gc.collect()

tab1, tab2, tab3 = st.tabs(["Playground", "Exercise", "Information"])

with tab3:

    st.markdown(
        "Let's start with just having some patients arriving into our treatment centre.")

    mermaid(height=350, code="""
            %%{ init: {  'flowchart': { 'curve': 'step'} } }%%

            %%{ init: {  'theme': 'base', 'themeVariables': {'lineColor': '#b4b4b4'} } }%%
            flowchart LR
            A[Arrival] --> B{Trauma or non-trauma}
            B --> B1{Trauma Pathway} 
            B --> B2{Non-Trauma Pathway}
                    
            B1 --> C[Stabilisation]
            C --> E[Treatment]
            E ----> F
                
            B2 --> D[Registration]
            D --> G[Examination]

            G --> H[Treat?]
            H ----> F[Discharge]
            H --> I[Non-Trauma Treatment]
            I --> F 

            C -.-> Z([Trauma Room])
            Z -.-> C

            E -.-> Y([Cubicle - 1])
            Y -.-> E

            D -.-> X([Clerks])
            X -.-> D

            G -.-> W([Exam Room])
            W -.-> G

            I -.-> V([Cubicle - 2])
            V -.-> I

            classDef highlight fill:#02CD55,stroke:#E8AD02,stroke-width:4px,color:#0C0D11,font-size:12pt,font-family:lexend;
            classDef unlight fill:#b4b4b4,stroke:#787878,stroke-width:2px,color:#787878,font-size:6pt,font-family:lexend;

            class A highlight;
            class B,B1,B2,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z unlight;

            
        """
            )
    
    st.markdown(
    """
    To start with, we need to create some simulated patients who will turn up to our centre. 

    To simulate patient arrivals, we will use the exponential distribution, which looks a bit like this. 

    """
    )
    
    exp_dist = Exponential(mean=5)
    exp_fig_example = px.histogram(exp_dist.sample(size=5000), 
                                 width=600, height=300)

    exp_fig_example.layout.update(showlegend=False, 
                            margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(exp_fig_example, use_container_width=True)

    st.markdown(
"""
To start with, we're just going to assume people arrive at a consistent rate throughout all 24 hours of the day. This isn't very realistic, but we can refine this later. 


When a patient arrives, the computer will pick a random number from this distribution to decide how long it will be before the next patient arrives at our treatment centre. 

Where the bar is very high, there is a high chance that the random number picked will be somewhere around that value. 

Where the bar is very low, it's very unlikely that the number picked will be from around that area - but it's not impossible. 

So what this ends up meaning is that, in this case, it's quite likely that the gap between each patient turning up at our centre will be somewhere between 0 and 10 minutes - and in fact, most of the time, someone will turn up every 2 or 3 minutes. However, now and again, we'll get a quiet period - and it might be 20 or 30 minutes until the next person arrives. 

This is quite realistic for a lot of systems - people tend to arrive fairly regularly, but sometimes the gap will be longer. 

As we get into more complex models, we can vary the distribution for different times of day or different months of the year so we can reflect real-world patterns better, but for now, we're just going to assume the arrival pattern is consistent. 

# Variability and Computers

Without getting too philosophical, the version of reality that happens is just one possible version!

Maybe we're going to get a really hot summer that means our department is busier due to heatstroke and people having accidents outside. 
Maybe it will rain all summer and everyone will stay indoors. 

And what if lots of people turn up really close together? How well does our department cope with that? 


So instead of just generating one set of arrivals, we will run the simulation multiple times. 

The first time the picks might be like this:

**5 minute gap, 4 minute gap, 5 minute gap, 6 minute gap**

The next time they might be like this:

**4 minute gap, 25 minute gap, 2 minute gap, 1 minute gap**

And so on. 

## Random seeds

Because computers aren't very good at being truly random, we give them a little nudge by telling them a 'random seed' to start from. 

You don't need to worry about how that works - but if our random seed is 1, we will draw a different set of times from our distribution to if our random seed is 100. 

This allows us to make lots of different realities! 
"""
    )


with tab2:

    st.subheader("Things to Try Out")

    st.markdown(
        """
        - Try changing the slider with the title 'How many patients should arrive per day on average?'. Look at the graph below it. How do the numbers on the horizontal axis change? Think about what effect this would have on your simulation.
        ---
        - Change the average number of patients back to the default (150) and click on 'Run simulation'. 
            - Look at the charts that show the variation in patient arrivals per simulation run. 
            - Look at the scatter (dot) plots at the bottom of the page to understand how the arrival times of patients varies across different simulation runs and different days. 
                - Hover over the dots to see more detail about the arrival time of each patient. By 6am, roughly how many patients have arrived in each simulation run? 
            - Think about how this randomness in arrival times across different runs could be useful.
        ---
        - Try changing the random number the computer uses without changing anything else. What happens to the number of patients? Do the bar charts and histograms look different?
        
        """)
    
    with st.expander("Click here for bonus exercises"):
        st.markdown(
            """
            ---        
            - Try running the simulation for under 5 days. What happens to the height of the bars in the first bar chart compared to running the simulation for more days? Are the bars larger or smaller? 
            ---
            - Try increasing the number of simulation runs. What do you notice about the *shape* of the histograms? Where are the bars highest?
            """
        )

with tab1:
    col1_1, col1_2= st.columns(2)
    # set number of resources
    with col1_1:
        seed = st.slider("🎲 Set a random number for the computer to start from",
                        1, 1000,
                        step=1, value=103)

        run_time_days = st.slider("🗓️ How many days should we run the simulation for each time?",
                                  1, 31,
                                  step=1, value=15)
        
        n_reps = st.slider("🔁 How many times should the simulation run?",
                           1, 25,
                           step=1, value=10)
        
        

    with col1_2:
        mean_arrivals_per_day = st.slider("🧍 How many patients should arrive per day on average?",
                                          10, 300,
                                          step=5, value=150)

        # Will need to convert mean arrivals per day into interarrival time and share that
        exp_dist = Exponential(mean=60/(mean_arrivals_per_day/24), random_seed=seed)
        exp_fig = px.histogram(exp_dist.sample(size=2500), 
                                width=500, height=250,
                                labels={
                     "value": "Inter-Arrival Time (Minutes)"
                 })
        
        exp_fig.update_layout(yaxis_title="")

        exp_fig.layout.update(showlegend=False, 
                              margin=dict(l=0, r=0, t=0, b=0))

        st.plotly_chart(exp_fig,
                        use_container_width=True,
                        config = {'displayModeBar': False})

        # set number of replication

    args = Scenario(random_number_set=seed, 
                    # We want to pass the interarrival time here
                    # To get from daily arrivals to average interarrival time,
                    # divide the number of arrivals by 24 to get arrivals per hour,
                    # then divide 60 by this value to get the number of minutes
                    manual_arrival_rate=60/(mean_arrivals_per_day/24),
                    override_arrival_rate=True)

    # A user must press a streamlit button to run the model
    button_run_pressed = st.button("Run simulation")

    if button_run_pressed:

        # add a spinner and then display success box
        with st.spinner('Simulating the minor injuries unit...'):
            # if not running_on_st_community:
            await asyncio.sleep(0.1)
            # run multiple replications of experment
            # results = multiple_replications(
            #     args,
            #     n_reps=n_reps,
            #     rc_period=run_time_days*60*24
            # )

            detailed_outputs = multiple_replications(
                args,
                n_reps=n_reps,
                rc_period=run_time_days*60*24,
                return_detailed_logs=True

            )

            patient_log = pd.concat([detailed_outputs[i]['results']['full_event_log'].assign(Rep= i+1) 
                            for i in range(n_reps)])

            results = pd.concat([detailed_outputs[i]['results']['summary_df'].assign(rep= i+1)
                                                for i in range(n_reps)]).set_index('rep')


            patient_log = patient_log.assign(model_day = (patient_log.time/24/60).pipe(np.floor)+1)
            patient_log = patient_log.assign(time_in_day= (patient_log.time - ((patient_log.model_day -1) * 24 * 60)).pipe(np.floor))
            # patient_log = patient_log.assign(time_in_day_ (patient_log.time_in_day/60).pipe(np.floor))
            patient_log['patient_full_id'] = patient_log['Rep'].astype(str) + '_' + patient_log['patient'].astype(str) 
            patient_log['rank'] = patient_log['time_in_day'].rank(method='max')

        #st.success('Done!')

        st.subheader(
            "Difference between average daily patients generated across simulation runs"
            )

        st.markdown(
            """
            The graph below shows the variation in the number of patients generated per day (on average) in a single simulation run. 
            This can help us understand how much variation we get between model runs when we don't change parameters, only the random seed.
            
            The height of each bar is relative to the **first** simulation run. 

            A bar that is **positive** shows that **more** patients were generated on average per day in that simulation than in the first simulation.
            
            A bar that is **negative** shows that **fewer* patients were generated on average per day in that simulation than in the first simulation.
            """
        )

        #progress_bar = st.progress(0)

        # This all used to work nicely when running in standard streamlit, but in stlite the animated element no longer works
        # So it's all a bit redundant and could be nicely simplified, but leaving for now as it works 

        # chart_mean_daily = st.bar_chart(results[['00_arrivals']].iloc[[0]]/run_time_days)
        # chart_mean_daily = st.bar_chart(
        #     results[['00_arrivals']].iloc[[0]] / run_time_days - results[['00_arrivals']].iloc[[0]] / run_time_days,

        #     height=250
            
        #     )
        # chart_total = st.bar_chart(results[['00_arrivals']].iloc[[0]])      

        results['00a_arrivals_difference'] = ((results[['00_arrivals']].iloc[0]['00_arrivals'].astype(int))/run_time_days) - (results['00_arrivals']/run_time_days) 

        results["colour_00a"] = np.where(results['00a_arrivals_difference']<0, 'neg', 'pos')
        # st.write(results)

        run_diff_bar_fig = px.bar(results.reset_index(drop=False), 
                                  x="rep", y='00a_arrivals_difference',
                                  color="colour_00a")

        run_diff_bar_fig.update_layout(
            yaxis_title="Difference in daily patients between first run and this run",
            xaxis_title="Simulation Run")
        
        
        run_diff_bar_fig.layout.update(showlegend=False)
        run_diff_bar_fig.update_xaxes(tick0=1, dtick=1)

        st.plotly_chart(
            run_diff_bar_fig, 
            use_container_width=True
            )

        # st.table(pd.concat([
        #         results[['00_arrivals']].astype('int'),
        #         (results[['00_arrivals']]/run_time_days).round(0).astype('int')
        #     ], axis=1, keys = ['Total Arrivals', 'Mean Daily Arrivals'])
        #         )

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
            # chart_mean_daily.add_rows(
            #     ((results[['00_arrivals']].iloc[[i+1]]['00_arrivals']/run_time_days) -
            #     (results[['00_arrivals']].iloc[0]['00_arrivals']/run_time_days)).round(1)
            # )

            status_text_string = 'Simulation {} generated a total of {} patients (an average of {} patients per day)'.format(
                    i+2,
                    new_rows.iloc[0]['00_arrivals'].astype(int),
                    (new_rows.iloc[0]['00_arrivals']/run_time_days).round(1)
                ) + "\n" + status_text_string 
            # Update status text.
            status_text.text(status_text_string)

        col_a_1, col_a_2 = st.columns(2)

        with col_a_1:
            st.subheader(
                "Histogram: Total Patients per Run"
            )

            st.markdown(
                """
                This plot shows the variation in the **total** daily patients per run. 
                
                The horizontal axis shows the range of patients generated within a simulation run.
                
                The height of the bar shows how many simulation runs had an output in that group."
                """
            )

            total_fig = px.histogram(
                        results[['00_arrivals']],
                        nbins=5
                        )
            total_fig.layout.update(showlegend=False)

            total_fig.update_layout(yaxis_title="Number of Simulation Runs",
                                    xaxis_title="Total Patients Generated in Run")

            st.plotly_chart(
                total_fig,
                use_container_width=True
            )
            
        with col_a_2:
            st.subheader(
                    "Histogram: Average Daily Patients per Run"
            )

            st.markdown(
                """
                This plot shows the variation in the **average** daily patients per run. 
                
                The horizontal axis shows the range of patients generated within a simulation run
                
                The height of the bar shows how many simulation runs had an output in that group.
                """
            )

            daily_average_fig = px.histogram(
                    (results[['00_arrivals']]/run_time_days).round(1),
                        nbins=5
                    )
            daily_average_fig.layout.update(showlegend=False)
            
            daily_average_fig.update_layout(yaxis_title="Number of Simulation Runs",
                                    xaxis_title="Average Daily Patients Generated in Run")

            st.plotly_chart(
                daily_average_fig,
                use_container_width=True
            )

        st.markdown(
            """
            The plots below show the minute-by-minute arrivals of patients across different model replications and different days.
            Only the first 10 replications and the first 5 days of the model are shown. 

            Each dot is a single patient arriving. 

            From left to right within each plot, we start at one minute past midnight and move through the day until midnight. 

            Looking from the top to the bottom of each plot, we have the model replications. 
            
            Each horizontal line of dots represents a **full day** for one model replication.  

            Hovering over the dots will show the exact time of each patient.
            """ 
        )

        #facet_col_wrap_calculated = np.ceil(run_time_days/4).astype(int)

        patient_log['minute'] = dt.date.today() + pd.DateOffset(days=165) +  pd.TimedeltaIndex(patient_log['time'], unit='m')
        # https://strftime.org/
        patient_log['minute_display'] = patient_log['minute'].apply(lambda x: dt.datetime.strftime(x, '%d %B %Y\n%H:%M'))
        # patient_log['minute'] = patient_log['minute'].apply(lambda x: dt.datetime.strftime(x, '%Y-%m-%d %H:%M'))


        for i in range(5):
            st.markdown("### Day {}".format(i+1))

            minimal_log = patient_log[(patient_log['event'] == 'arrival') & 
                                    (patient_log['Rep'] <= 10) & 
                                    (patient_log['model_day'] == i+1)]
            
            minimal_log['Rep_str'] = minimal_log['Rep'].astype(str)

            time_plot = px.scatter(
                    minimal_log.sort_values("minute"),
                    x="minute", 
                    y="Rep",
                    color="Rep_str",
                    custom_data=["minute_display", "patient"],
                    category_orders={'Rep_str': [str(i+1) for i in range(10)]},
                    range_y=[0.5, min(10, n_reps)+0.5],
                    width=1200,
                    height=300,
                    opacity=0.5
            )
            
            del minimal_log
            
            def format_date_with_ordinal(d, format_string):
                ordinal = {'1':'st', '2':'nd', '3':'rd'}.get(str(d.day)[-1:], 'th')
                return d.strftime(format_string).replace('{th}', ordinal)


            time_plot.update_traces(
                hovertemplate="<br>".join([
                    "Time of patient arrival: %{customdata[0]}",
                    "Arrival in this simulation run: %{customdata[1]}"
                ])
            )

            time_plot.update_layout(yaxis_title="Simulation Run (Replication)",
                                    xaxis_title="Time",
                        yaxis = dict(
                        tickmode = 'linear',
                        tick0 = 1,
                        dtick = 1
                    ))
            
            time_plot.layout.update(showlegend=False, 
                                    margin=dict(l=0, r=0, t=0, b=0))
            
            st.plotly_chart(time_plot, use_container_width=True)

    gc.collect()
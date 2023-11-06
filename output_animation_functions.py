import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def reshape_for_animations(full_event_log):
    minute_dfs = list()
    patient_dfs = list()

    for rep in range(1, max(full_event_log['rep'])+1):
        # print("Rep {}".format(rep))
        # Start by getting data for a single rep
        filtered_log_rep = full_event_log[full_event_log['rep'] == rep]
        pivoted_log = filtered_log_rep.pivot_table(values="time", 
                                            index=["patient","event_type","pathway"], 
                                            columns="event").reset_index()

        for minute in range(10*60*24):
            # print(minute)
            # Get patients who arrived before the current minute and who left the system after the current minute
            # (or arrived but didn't reach the point of being seen before the model run ended)
            # When turning this into a function, think we will want user to pass
            # 'first step' and 'last step' or something similar
            # and will want to reshape the event log for this so that it has a clear start/end regardless
            # of pathway (move all the pathway stuff into a separate column?)

            # Think we maybe need a pathway order and pathway precedence column
            # But what about shared elements of each pathway?
            if minute % 10 == 0:

                try:
                    current_patients_in_moment = pivoted_log[(pivoted_log['arrival'] <= minute) & 
                                (
                                    (pivoted_log['depart'] >= minute) |
                                    (pivoted_log['depart'].isnull() )
                                )]['patient'].values
                except KeyError:
                    current_patients_in_moment = None
                
                if current_patients_in_moment is not None:
                    patient_minute_df = filtered_log_rep[filtered_log_rep['patient'].isin(current_patients_in_moment)]
                    # print(len(patient_minute_df))
                    # Grab just those clients from the filtered log (the unpivoted version)
                    # Each person can only be in a single place at once, so filter out any events
                    # that have taken place after the minute
                    # then just take the latest event that has taken place for each client
                    # most_recent_events_minute = patient_minute_df[patient_minute_df['time'] <= minute] \
                    #     .sort_values('time', ascending=True) \
                    #     .groupby(['patient',"event_type","pathway"]) \
                    #     .tail(1)  

                    most_recent_events_minute_ungrouped = patient_minute_df[patient_minute_df['time'] <= minute] \
                        .sort_values('time', ascending=True) \
                        .groupby(['patient']) \
                        .tail(1) 

                    patient_dfs.append(most_recent_events_minute_ungrouped.assign(minute=minute, rep=rep))

                    # Now count how many people are in each state
                    # CHECK - I THINK THIS IS PROBABLY DOUBLE COUNTING PEOPLE BECAUSE OF THE PATHWAY AND EVENT TYPE. JUST JOIN PATHWAY/EVENT TYPE BACK IN INSTEAD?
                    state_counts_minute = most_recent_events_minute_ungrouped[['event']].value_counts().reset_index().assign(minute=minute, rep=rep)
                    
                    minute_dfs.append(state_counts_minute)


    minute_counts_df = pd.concat(minute_dfs).merge(filtered_log_rep[['event','event_type', 'pathway']].drop_duplicates().reset_index(drop=True), on="event")
    full_patient_df = pd.concat(patient_dfs).sort_values(["rep", "minute", "event"])


    minute_counts_df_pivoted = minute_counts_df.pivot_table(values="count", 
                                            index=["minute", "rep","event_type","pathway"], 
                                            columns="event").reset_index().fillna(0)

    minute_counts_df_complete = minute_counts_df_pivoted.melt(id_vars=["minute", "rep","event_type","pathway"])

    return {
        "minute_counts_df": minute_counts_df,
        "minute_counts_df_complete": minute_counts_df_complete,
        "full_patient_df": full_patient_df
        
    }


# ['TRAUMA_triage_wait_begins', 'TRAUMA_triage_begins', 'TRAUMA_triage_complete', 
#                                     'TRAUMA_stabilisation_wait_begins', 'TRAUMA_stabilisation_begins', 'TRAUMA_stabilisation_complete', 
#                                     'TRAUMA_treatment_wait_begins', 'TRAUMA_treatment_begins', 'TRAUMA_treatment_wait_begins'
#                                     ]

def animate_queue_activity_bar_chart(minute_counts_df_complete,
                                     event_order, 
                                     rep=1):
    # Downsample to only include a snapshot every 10 minutes (else it falls over completely)
    # For runs of more days will have to downsample more aggressively - every 10 minutes works for 15 days
    fig = px.bar(minute_counts_df_complete[minute_counts_df_complete["rep"] == int(rep)].sort_values('minute'), 
                x="event", 
                y="value", 
                animation_frame="minute", 
                range_y=[0,minute_counts_df_complete['value'].max()*1.1])



    fig.update_xaxes(categoryorder='array', 
                    categoryarray= event_order)
    
    fig["layout"].pop("updatemenus")
    
    return fig


def animate_activity_log(
        full_patient_df,
        event_position_df,
        scenario,
        rep=1,
        plotly_height=900,
        wrap_queues_at = None,
        include_play_button=False      
        ):
    """_summary_

    Args:
        full_patient_df (pd.Dataframe): _description_
        event_position_dicts (pd.Dataframe): 
            dataframe with three cols - event, x and y
            Can be more easily created by passing a list of dicts to pd.DataFrame
            list of dictionaries with one dicitionary per event type
            containing keys 'event', 'x' and 'y'
            This will determine the intial position of any entries in the animated log



        rep (int, optional): _description_. Defaults to 1.
        plotly_height (int, optional): _description_. Defaults to 900.

    Returns:
        _type_: _description_
    """        
    
    

    full_patient_df = full_patient_df[full_patient_df['rep'] == rep].sort_values('minute')

    full_patient_df['count'] = full_patient_df.groupby(['event','minute','rep'])['minute'].transform('count')
    full_patient_df['rank'] = full_patient_df.groupby(['event','minute','rep'])['minute'].rank(method='first')


    full_patient_df_plus_pos = full_patient_df.merge(event_position_df, on="event")

    full_patient_df_plus_pos['y_final'] =  full_patient_df_plus_pos['y']
    full_patient_df_plus_pos['x_final'] = full_patient_df_plus_pos['x'] - full_patient_df_plus_pos['rank']*10

    # full_patient_df_plus_pos['icon'] = '🙍'

    individual_patients = full_patient_df['patient'].drop_duplicates().sort_values()
    icon_list = ['🧔🏼', '🧑🏾‍🦯', '👨🏻‍🦰', '🧑🏻', '👩🏿‍🦱', '🧑🏻‍🍼', '👳🏽', '👩🏼‍🦳', '👨🏿‍🦳', '🧑🏻‍🦱', '🧍🏽‍♀️', '🧑🏼‍🔬', '👩🏻‍🦰', '🧕🏿', '🧑‍🦽', '👴🏾'
                 '🧑🏼‍🦱', '👷🏾', '🧑🏻‍🦲', '🧑🏿‍💼',  '🧔🏾', '🧕🏻', '👨🏾‍🎓', '👴🏻', '🧍🏼‍♂️', '👧🏿', '🙎🏻',  '🧑🏿‍🦱', '👱🏻', '🙋🏾‍♀️', '🧑🏼‍🔧', '🧑🏿‍🦽', '🧑🏽‍🦳'
                 '🧑‍🦼', '🙋🏽‍♂️', '👩🏿‍🎓', '🤷🏻', '👶🏾', '🧑🏻‍✈️', '🙎🏾', '👶🏻', '👴🏿', '👨🏻‍🦳', '👩🏽', '🧑🏻‍🦳', '👩🏽‍🎓', '👱🏻‍♀️', '👲🏼', '🧕🏾', 
                 '🧑‍🦯', '🧔🏿', '👳🏿', '🧑🏿‍🍼', '👩🏽‍🦰', '🧑🏾‍🦲', '🧍🏾‍♂️', '👧🏼', '🤷🏿‍♂️', '🧑🏻‍✈️', '👱🏾‍♂️', '👨🏻‍🎓', '👵🏼', '🤵🏿', '👳🏻', '🙋🏼',
                 '👩🏻‍🎓', '🧑🏻‍🌾', '👩🏿‍🔧', '🤵🏻', '🧑🏼‍💼', '🧑🏿‍✈️', '🎅🏼'
    ]

    full_icon_list = icon_list * int(np.ceil(len(individual_patients)/len(icon_list)))

    full_icon_list = full_icon_list[0:len(individual_patients)]

    full_patient_df_plus_pos = full_patient_df_plus_pos.merge(
        pd.DataFrame({'patient':list(individual_patients), 
                      'icon':full_icon_list}),
        on="patient")


    full_patient_df_plus_pos['size'] = 24
    # First add the animated traces for the different resources
    fig = px.scatter(
            full_patient_df_plus_pos.sort_values('minute'), 
            x="x_final", 
            y="y_final", 
            animation_frame="minute", 
            animation_group="patient",
            text="icon",
            # Can't have colours because it causes bugs with
            # lots of points failing to appear
            #color="event", 
            hover_name="event",
            hover_data=["patient", "pathway", "time", "minute"],
            #    symbol="rep",
            #    symbol_sequence=["⚽"],
            #symbol_map=dict(rep_choice = "⚽"),
            range_x=[0, event_position_df['x'].max()*1.25], 
            range_y=[0, [0, event_position_df['y'].max()*1.1]],
            height=plotly_height,
            #    size="size"
            )

    # Update the size of the icons
    fig.update_traces(textfont_size=24)
    
    # Now add labels identifying each stage
    fig.add_trace(go.Scatter(
        x=event_position_df['x'].to_list(),
        y=event_position_df['y'].to_list(),
        mode="text",
        name="",
        text=event_position_df['label'].to_list(),
        textposition="middle right",
        hoverinfo='none'
    ))

    events_with_resources = event_position_df[event_position_df['resource'].notnull()].copy()
    
    
    # Finally add in icons to indicate the available resources
    # Make an additional dataframe that has one row per resource type
    # Then, starting from the initial position, make that many large circles
    # make them semi-transparent or you won't see the people using them! 

    events_with_resources['resource_count'] = events_with_resources['resource'].apply(lambda x: getattr(scenario, x))

    events_with_resources = events_with_resources.join(events_with_resources.apply(
        lambda r: pd.Series({'x_final': [r['x']-(10*(i+1)) for i in range(r['resource_count'])]}), axis=1).explode('x_final'),
        how='right')

    fig.add_trace(go.Scatter(
        x=events_with_resources['x_final'].to_list(),
        y=events_with_resources['y'].to_list(),
        mode="markers",
        marker=dict(
            color='LightSkyBlue',
            size=15),
        opacity=0.3,
        hoverinfo='none'
        # name="",
        # textposition="middle right"
    ))

    fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_layout(yaxis_title=None, xaxis_title=None)

    if not include_play_button:
        fig["layout"].pop("updatemenus")

    return fig

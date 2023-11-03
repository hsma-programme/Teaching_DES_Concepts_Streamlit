import plotly.express as px
import pandas as pd


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
                    most_recent_events_minute = patient_minute_df[patient_minute_df['time'] <= minute] \
                        .sort_values('time', ascending=True) \
                        .groupby(['patient',"event_type","pathway"]) \
                        .tail(1)  

                    patient_dfs.append(most_recent_events_minute.assign(minute=minute, rep=rep))

                    # Now count how many people are in each state
                    state_counts_minute = most_recent_events_minute[['pathway', 'event_type','event']].value_counts().reset_index().assign(minute=minute, rep=rep)
                    
                    minute_dfs.append(state_counts_minute)


    minute_counts_df = pd.concat(minute_dfs)
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
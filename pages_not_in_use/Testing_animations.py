import streamlit as st

from helper_functions import read_file_contents, add_logo, mermaid
from model_classes import *
# from st_pages import show_pages_from_config, add_page_title
import plotly.express as px
import drawsvg as dw
from streamlit.components.v1 import html
import plotly.graph_objects as go

st.set_page_config(
     page_title="The Full Model",
     layout="wide",
     initial_sidebar_state="expanded",
 )

add_logo()

with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

## We add in a title for our web app's page
st.title("Discrete Event Simulation Playground")
st.subheader("How can we optimise the full system?")

args = Scenario()

# args.n_triage

n_reps = 2
rc_period = 10*60*24

detailed_outputs = multiple_replications(
            scenario=args,
            n_reps=n_reps,
            rc_period=rc_period,
            return_detailed_logs=True
        )

#detailed_outputs[1]['results']['utilisation_audit']

patient_log = pd.concat([detailed_outputs[i]['results']['full_event_log'].assign(Rep= i+1) 
                         for i in range(n_reps)])

full_utilisation_audit = pd.concat([detailed_outputs[i]['results']['utilisation_audit'].assign(Rep= i+1)
                                    for i in range(n_reps)])


# st.write(patient_log)


# patient_log['event'].value_counts()

# I think what we need to do is have key frames for the different states of the model
# Or we iterate through the minutes of the model and generate the frame based on where everyone is at that precise moment in time
# Let's start with a subset of states: arriving, queuing for trauma stabilisation, queueing for trauma treatment, exiting
# Here we're not going to think about people accessing different resources (e.g. if we've got 2 rooms - we're just looking at them getting through the system)


filtered_log = patient_log[
    patient_log['event'].str.contains("TRAUMA")
]

# filtered_log['event'].value_counts()

# filtered_log[filtered_log['patient'] == 18]



# Steps - generating keyframes
# Work out where everyone is at a given moment (1 minute increments)
# Generate each frame, with a queue of people waiting by each resource

# Iterating by minute
# To get who is in the system, start by excluding any patients who have either not yet arrived or who have left
# Then pivot so we have a count of who is at each resource

# Have a standardised template for the resource layout
# (later we can make this adjust to the number of resources that are set up by the user)
# Maybe put a box around each group of resources and head it up with the stage
# Stages are hardcoded (later can expand this to be more clever)
# But then within each box it can be programatically expanded based on slider/scenario inputs


# Get various details from the scenario object


# Set up an empty list for the minute-by-minute df
minute_dfs = list()
patient_dfs = list()

# First set up the canvas and animation controls
d = dw.Drawing(1000, 800, origin=(0, 0),
        animation_config=dw.types.SyncedAnimationConfig(
            # Animation configuration
            duration=(10*60*24)/100,  # Seconds
            show_playback_progress=True,
            show_playback_controls=True))

d.append(dw.Rectangle(0, 0, 1000, 800, fill='#eee'))  # Background

for rep in range(1, max(filtered_log['Rep'])+1):
    # print("Rep {}".format(rep))
    # Start by getting data for a single rep
    filtered_log_rep = filtered_log[filtered_log['Rep'] == rep]
    pivoted_log = filtered_log_rep.pivot_table(values="time", 
                                           index="patient", 
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
                current_patients_in_moment = pivoted_log[(pivoted_log['TRAUMA_triage_wait_begins'] <= minute) & 
                            (
                                (pivoted_log['TRAUMA_treatment_complete'] >= minute) |
                                (pivoted_log['TRAUMA_treatment_complete'].isnull() )
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
                    .groupby('patient') \
                    .tail(1)  

                patient_dfs.append(most_recent_events_minute.assign(minute=minute, rep=rep))

                # Now count how many people are in each state
                state_counts_minute = most_recent_events_minute['event'].value_counts().reset_index().assign(minute=minute, rep=rep)
                
                minute_dfs.append(state_counts_minute)
                
                
                # Set up the layout of the flow
                # In future this will be done programatically, but for now let's just do it fairly simply
                # For our triage pathway, we need people to be in the following states
                # - arriving (waiting for triage)
                # - being triaged
                # - waiting for stabilisation
                # - being stabilised
                # - waiting for treatment
                # - being treated
                # - being discharged
                # For now, let's make sections squares and people circles

                # set up triage waits
                

                # set up triage

                # set up stabilisation waits


                # Set up stabilisation


                # Set up waiting for treatment
                    # if len(state_counts_minute) > 0:
                    #     try:
                    #         for i in range(1, state_counts_minute[state_counts_minute["event"]=="TRAUMA_triage_begins"].iloc[0]['count']):
                    #             circle = dw.Circle(100, 100, 10, fill='gray')  # Moving circle
                    #             circle.add_key_frame(minute, cx=100, cy=100)
                    #             d.append(circle)
                    #     except IndexError:
                    #         pass



                # Set up being treated

# html(d.as_html(), width=1100, height=900)

# st.write(pd.concat(minute_dfs))



rep_choice = st.selectbox(label="Select the replication to explore",
             options=range(1, n_reps+1))

minute_counts_df = pd.concat(minute_dfs)
full_patient_df = pd.concat(patient_dfs).sort_values(["rep", "minute", "event"])


minute_counts_df_pivoted = minute_counts_df.pivot_table(values="count", 
                                           index=["minute", "rep"], 
                                           columns="event").reset_index().fillna(0)

minute_counts_df_complete = minute_counts_df_pivoted.melt(id_vars=["minute", "rep"])
minute_counts_df_downsampled = minute_counts_df_complete[minute_counts_df_complete["minute"] % 10 == 0 ] 

# Downsample to only include a snapshot every 10 minutes (else it falls over completely)
# For runs of more days will have to downsample more aggressively - every 10 minutes works for 15 days
fig = px.bar(minute_counts_df_downsampled[minute_counts_df_downsampled["rep"] == int(rep_choice)].sort_values('minute'), 
             x="event", 
             y="value", 
             animation_frame="minute", 
             range_y=[0,minute_counts_df['count'].max()*1.1])



fig.update_xaxes(categoryorder='array', 
                 categoryarray= ['TRAUMA_triage_wait_begins', 'TRAUMA_triage_begins', 'TRAUMA_triage_complete', 
                                 'TRAUMA_stabilisation_wait_begins', 'TRAUMA_stabilisation_begins', 'TRAUMA_stabilisation_complete', 
                                 'TRAUMA_treatment_wait_begins', 'TRAUMA_treatment_begins', 'TRAUMA_treatment_wait_begins'
                                 ])

st.subheader("Event Log Animation 1")

# Remove the play/pause buttton and just keep the drag as then it looks less like people are moving
# backwards and forwards between stages
# https://stackoverflow.com/questions/68624485/hide-play-and-stop-buttons-in-plotly-express-animation

fig["layout"].pop("updatemenus")

st.plotly_chart(fig,
           use_container_width=True)


# df = minute_counts_df_pivoted[minute_counts_df_pivoted["minute"] % 10 == 0 ]

full_patient_df.value_counts('event')


full_patient_df['count'] = full_patient_df.groupby(['event','minute','rep'])['minute'].transform('count')
full_patient_df['rank'] = full_patient_df.groupby(['event','minute','rep'])['minute'].rank(method='first')





event_position_dicts = pd.DataFrame([
    {'event': 'arrival', 'x':  50, 'y': 15 },
    {'event': 'TRAUMA_triage_wait_begins', 'x':  100, 'y': 30 },
    {'event': 'TRAUMA_triage_begins', 'x':  150, 'y': 60 },
    {'event': 'TRAUMA_triage_complete', 'x':  200, 'y': 90},
    {'event': 'TRAUMA_stabilisation_wait_begins', 'x': 250, 'y': 120},
    {'event': 'TRAUMA_stabilisation_begins', 'x': 300, 'y': 150},
    {'event': 'TRAUMA_stabilisation_complete', 'x': 350, 'y': 180},
    {'event': 'TRAUMA_treatment_wait_begins', 'x': 400, 'y': 210},
    {'event': 'TRAUMA_treatment_begins', 'x': 450, 'y': 240}
])

full_patient_df_plus_pos = full_patient_df.merge(event_position_dicts, on="event")

full_patient_df_plus_pos['y_final'] =  full_patient_df_plus_pos['y']
full_patient_df_plus_pos['x_final'] = full_patient_df_plus_pos['x'] - full_patient_df_plus_pos['rank']*5


# This is very slow!
full_patient_df_plus_pos['label'] = np.where(full_patient_df_plus_pos['x_final'].astype(int) == full_patient_df_plus_pos['x'].astype(int)-5, 
                                             full_patient_df_plus_pos['event'], 
                                             '')

# Hacky workaround for making the icons people, not shapes

# choose an icon from https://www.compart.com/en/unicode/search?q=person#characters
# idea taken from Blueberry's comment here https://community.plotly.com/t/i-want-to-use-custom-icon-for-the-scatter-markers-how-to-do-it/6644/4
full_patient_df_plus_pos['icon'] = '🙍'
full_patient_df_plus_pos['size'] = 24

fig2 = px.scatter(
           full_patient_df_plus_pos[full_patient_df_plus_pos["rep"] == int(rep_choice)].sort_values('minute'), 
           x="x_final", 
           y="y_final", 
           animation_frame="minute", 
           animation_group="patient",
           text="icon",
           # Can't have colours because it causes bugs with
           # lots of points failing to appear
           #color="event", 
           hover_name="event",
        #    symbol="rep",
        #    symbol_sequence=["⚽"],
           #symbol_map=dict(rep_choice = "⚽"),
           range_x=[0, 550], range_y=[0,300],
           height=900,
        #    size="size"
           )

# Update the size of the icons
fig2.update_traces(textfont_size=24)

fig2.add_trace(go.Scatter(
    x=event_position_dicts['x'].to_list(),
    y=event_position_dicts['y'].to_list(),
    mode="text",
    name="",
    text=event_position_dicts['event'].to_list(),
    textposition="middle right"
))

fig2.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
fig2.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
fig2.update_layout(yaxis_title=None, xaxis_title=None)

# fig2.update_layout(
#     font=dict(
#         size=24
#     )
# )

# Remove the play/pause buttton and just keep the drag as then it looks less like people are moving
# backwards and forwards between stages
# https://stackoverflow.com/questions/68624485/hide-play-and-stop-buttons-in-plotly-express-animation

fig2["layout"].pop("updatemenus")

# fig2.update_traces(
#     textposition='top center'
#     )

st.subheader("Event Log Animation 2")

st.plotly_chart(fig2,
           use_container_width=True)
st.markdown("""
            To do:
            - ~~add in labels to make it clear what each step is doing (I sacrificed this to be able to have people icons, but original approach did have the issue of the labels disappearing if there was no-one in at that point anyway)~~
            - split out and visualise the available resources at each step
            - tweak the event log in models_classes.py to split out pathways
            - generalise into a function (which will also expand it to deal with the additional steps in this pathway)
            - consider how to best lay out - e.g. do we create groups of 5 or 10 people that then cascade down vertically instead of creating a neverending horizontal queue that is hard to count? (and can go off the plot?)
            
            With regards to getting the animation to look at which resources are in use at the time, it's going to be a bit tricky
            with the way it's currently written because it seems like it's not really supported to monitor which resource people are
            accessing from a pool, so resources have to be rewritten to be a store. 

            https://stackoverflow.com/questions/39956444/simpy-resource-get-id
            https://stackoverflow.com/questions/74803930/how-can-i-print-with-simpy-which-resource-each-customer-goes-to
            https://stackoverflow.com/questions/66405873/how-to-know-which-resource-is-being-used-when-using-simpys-simpy-events-anyof
            
            I don't think it's worth rewriting to use this for now as it complicates the understanding of resources (if people are inclined
            to look at the code) and it doesn't add enough benefit vs 

            Can't do a simple fudge by randomising the position of users when count changes BUT could potentially use the 
            full patient log 

            """)


st.subheader("Utilisation Log Animation")

full_utilisation_audit['number_not_utilised'] = full_utilisation_audit['number_available'] - full_utilisation_audit['number_utilised'] 



fig3 = px.bar(
           full_utilisation_audit[['resource_name', 'simulation_time', 'number_utilised', 'number_not_utilised']].melt(id_vars=['resource_name', 'simulation_time']), 
           x="resource_name", 
           y="value",
           color="variable", 
           animation_frame="simulation_time", 
        #    animation_group="resource_name",
        #    text="icon",
           # Can't have colours because it causes bugs with
           # lots of points failing to appear
           #color="event", 
        #    hover_name="event",
        #    symbol="rep",
        #    symbol_sequence=["⚽"],
           #symbol_map=dict(rep_choice = "⚽"),
           range_y=[0,5],
           height=900,
        #    size="size"
           )

fig3["layout"].pop("updatemenus")


st.plotly_chart(fig3,
           use_container_width=True)

# full_patient_df_plus_pos[full_patient_df_plus_pos['minute']==11380].sort_values(['y_final', 'x_final'])
# tab1, tab2, tab3, tab4 = st.tabs(["Anim 1", "Anim 2", "Anim 3", "Anim 4"])

# with tab1:

#     d = dw.Drawing(200, 200, origin='center')

#     # Animate the position and color of circle
#     c = dw.Circle(0, 0, 20, fill='red')
#     # See for supported attributes:
#     # https://developer.mozilla.org/en-US/docs/Web/SVG/Element/animate
#     c.append_anim(dw.Animate('cy', '6s', '-80;80;-80',
#                             repeatCount='indefinite'))
#     c.append_anim(dw.Animate('cx', '6s', '0;80;0;-80;0',
#                             repeatCount='indefinite'))
#     c.append_anim(dw.Animate('fill', '6s', 'red;green;blue;yellow',
#                             calc_mode='discrete',
#                             repeatCount='indefinite'))
#     d.append(c)

#     # Animate a black circle around an ellipse
#     ellipse = dw.Path()
#     ellipse.M(-90, 0)
#     ellipse.A(90, 40, 360, True, True, 90, 0)  # Ellipse path
#     ellipse.A(90, 40, 360, True, True, -90, 0)
#     ellipse.Z()
#     c2 = dw.Circle(0, 0, 10)
#     # See for supported attributes:
#     # https://developer.mozilla.org/en-US/docs/Web/SVG/Element/animate_motion
#     c2.append_anim(dw.AnimateMotion(ellipse, '3s',
#                                     repeatCount='indefinite'))
#     # See for supported attributes:
#     # https://developer.mozilla.org/en-US/docs/Web/SVG/Element/animate_transform
#     c2.append_anim(dw.AnimateTransform('scale', '3s', '1,2;2,1;1,2;2,1;1,2',
#                                         repeatCount='indefinite'))
#     d.append(c2)

#     html(d.as_html(), width=220, height=220)

# with tab2:
#     d = dw.Drawing(400, 200, origin='center',
#         animation_config=dw.types.SyncedAnimationConfig(
#             # Animation configuration
#             duration=8,  # Seconds
#             show_playback_progress=True,
#             show_playback_controls=True))
#     d.append(dw.Rectangle(-200, -100, 400, 200, fill='#eee'))  # Background
#     d.append(dw.Circle(0, 0, 40, fill='green'))  # Center circle

#     # Animation
#     circle = dw.Circle(0, 0, 0, fill='gray')  # Moving circle
#     circle.add_key_frame(0, cx=-100, cy=0,    r=0)
#     circle.add_key_frame(2, cx=0,    cy=-100, r=40)
#     circle.add_key_frame(4, cx=100,  cy=0,    r=0)
#     circle.add_key_frame(6, cx=0,    cy=100,  r=40)
#     circle.add_key_frame(8, cx=-100, cy=0,    r=0)
#     d.append(circle)
#     r = dw.Rectangle(0, 0, 0, 0, fill='silver')  # Moving square
#     r.add_key_frame(0, x=-100, y=0,       width=0,  height=0)
#     r.add_key_frame(2, x=0-20, y=-100-20, width=40, height=40)
#     r.add_key_frame(4, x=100,  y=0,       width=0,  height=0)
#     r.add_key_frame(6, x=0-20, y=100-20,  width=40, height=40)
#     r.add_key_frame(8, x=-100, y=0,       width=0,  height=0)
#     d.append(r)

#     # Changing text
#     dw.native_animation.animate_text_sequence(
#             d,
#             [0, 2, 4, 6],
#             ['0', '1', '2', '3'],
#             30, 0, 1, fill='yellow', center=True)

#     html(d.as_html(), width=420, height=320)

# import base64

#d.save_svg('animated.svg')  # Save to file
# def render_svg(svg):
#     """Renders the given svg string."""
#     b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
#     html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
#     st.write(html, unsafe_allow_html=True)

# render_svg(d)
# Get the resource objects out of the scenario

# args.

# # Define the order of events in a dictionary
# events_ordering = {
#     arrival
# }

# with tab3:
#     # Let's borrow the man icon from the docs
#     d = dw.Drawing(200, 200, origin='center')

#     g_man = dw.Group(id='man', fill='none', stroke='blue')
#     g_man.append(dw.Circle(85, 56, 10))
#     g_man.append(dw.Line(85, 66, 85, 80))
#     g_man.append(dw.Lines(76, 104, 85, 80, 94, 104))
#     g_man.append(dw.Lines(76, 70, 85, 76, 94, 70))
#     d.append(g_man)

#     html(d.as_html(), width=220, height=220)


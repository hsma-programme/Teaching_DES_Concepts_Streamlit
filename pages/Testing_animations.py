import streamlit as st

from helper_functions import read_file_contents, add_logo, mermaid
from model_classes import *
# from st_pages import show_pages_from_config, add_page_title
import plotly.express as px
import drawsvg as dw
from streamlit.components.v1 import html

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

patient_log = multiple_replications(
            scenario=args,
            n_reps=2,
            rc_period=10*60*24,
            return_event_log=True
        )

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

# First set up the canvas and animation controls
d = dw.Drawing(1000, 800, origin=(0, 0),
        animation_config=dw.types.SyncedAnimationConfig(
            # Animation configuration
            duration=(10*60*24)/100,  # Seconds
            show_playback_progress=True,
            show_playback_controls=True))

d.append(dw.Rectangle(0, 0, 1000, 800, fill='#eee'))  # Background

for rep in range(1, max(filtered_log['Rep'])):
    # print("Rep {}".format(rep))
    # Start by getting data for a single rep
    filtered_log_rep = filtered_log[filtered_log['Rep'] == 1]
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

            # Now count how many people are in each state
            state_counts_minute = most_recent_events_minute['event'].value_counts().reset_index().assign(minute=minute)
            
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
            if len(state_counts_minute) > 0:
                try:
                    for i in range(1, state_counts_minute[state_counts_minute["event"]=="TRAUMA_triage_begins"].iloc[0]['count']):
                        circle = dw.Circle(100, 100, 10, fill='gray')  # Moving circle
                        circle.add_key_frame(minute, cx=100, cy=100)
                        d.append(circle)
                except IndexError:
                    pass



        # Set up being treated

# html(d.as_html(), width=1100, height=900)

# st.write(pd.concat(minute_dfs))

minute_counts_df = pd.concat(minute_dfs)

minute_counts_df_pivoted = minute_counts_df.pivot_table(values="count", 
                                           index="minute", 
                                           columns="event").reset_index().fillna(0)

minute_counts_df_complete = minute_counts_df_pivoted.melt(id_vars="minute")


# Downsample to only include a snapshot every 10 minutes (else it falls over completely)
# For runs of more days will have to downsample more aggressively - every 10 minutes works for 15 days
fig = px.bar(minute_counts_df_complete[minute_counts_df_complete["minute"] % 10 == 0 ] , 
             x="event", 
             y="value", 
             animation_frame="minute", 
             range_y=[0,minute_counts_df['count'].max()*1.1])



st.plotly_chart(fig)


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

with tab3:
    # Let's borrow the man icon from the docs
    d = dw.Drawing(200, 200, origin='center')

    g_man = dw.Group(id='man', fill='none', stroke='blue')
    g_man.append(dw.Circle(85, 56, 10))
    g_man.append(dw.Line(85, 66, 85, 80))
    g_man.append(dw.Lines(76, 104, 85, 80, 94, 104))
    g_man.append(dw.Lines(76, 70, 85, 76, 94, 70))
    d.append(g_man)

    html(d.as_html(), width=220, height=220)


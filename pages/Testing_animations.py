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

st.write(patient_log)


patient_log['event'].value_counts()

# I think what we need to do is have key frames for the different states of the model
# Or we iterate through the minutes of the model and generate the frame based on where everyone is at that precise moment in time
# Let's start with a subset of states: arriving, queuing for trauma stabilisation, queueing for trauma treatment, exiting
# Here we're not going to think about people accessing different resources (e.g. if we've got 2 rooms - we're just looking at them getting through the system)


filtered_log = patient_log[
    patient_log['event'].str.contains("TRAUMA")
]

filtered_log['event'].value_counts()

filtered_log[filtered_log['patient'] == 18]

# Let's borrow the man icon from the docs

d = dw.Drawing(200, 200, origin='center')

g_man = dw.Group(id='man', fill='none', stroke='blue')
g_man.append(dw.Circle(85, 56, 10))
g_man.append(dw.Line(85, 66, 85, 80))
g_man.append(dw.Lines(76, 104, 85, 80, 94, 104))
g_man.append(dw.Lines(76, 70, 85, 76, 94, 70))
d.append(g_man)

html(d.as_html(), width=220, height=220)

tab1, tab2, tab3, tab4 = st.tabs(["Anim 1", "Anim 2", "Anim 3", "Anim 4"])

with tab1:

    d = dw.Drawing(200, 200, origin='center')

    # Animate the position and color of circle
    c = dw.Circle(0, 0, 20, fill='red')
    # See for supported attributes:
    # https://developer.mozilla.org/en-US/docs/Web/SVG/Element/animate
    c.append_anim(dw.Animate('cy', '6s', '-80;80;-80',
                            repeatCount='indefinite'))
    c.append_anim(dw.Animate('cx', '6s', '0;80;0;-80;0',
                            repeatCount='indefinite'))
    c.append_anim(dw.Animate('fill', '6s', 'red;green;blue;yellow',
                            calc_mode='discrete',
                            repeatCount='indefinite'))
    d.append(c)

    # Animate a black circle around an ellipse
    ellipse = dw.Path()
    ellipse.M(-90, 0)
    ellipse.A(90, 40, 360, True, True, 90, 0)  # Ellipse path
    ellipse.A(90, 40, 360, True, True, -90, 0)
    ellipse.Z()
    c2 = dw.Circle(0, 0, 10)
    # See for supported attributes:
    # https://developer.mozilla.org/en-US/docs/Web/SVG/Element/animate_motion
    c2.append_anim(dw.AnimateMotion(ellipse, '3s',
                                    repeatCount='indefinite'))
    # See for supported attributes:
    # https://developer.mozilla.org/en-US/docs/Web/SVG/Element/animate_transform
    c2.append_anim(dw.AnimateTransform('scale', '3s', '1,2;2,1;1,2;2,1;1,2',
                                        repeatCount='indefinite'))
    d.append(c2)

    html(d.as_html(), width=220, height=220)

with tab2:
    d = dw.Drawing(400, 200, origin='center',
        animation_config=dw.types.SyncedAnimationConfig(
            # Animation configuration
            duration=8,  # Seconds
            show_playback_progress=True,
            show_playback_controls=True))
    d.append(dw.Rectangle(-200, -100, 400, 200, fill='#eee'))  # Background
    d.append(dw.Circle(0, 0, 40, fill='green'))  # Center circle

    # Animation
    circle = dw.Circle(0, 0, 0, fill='gray')  # Moving circle
    circle.add_key_frame(0, cx=-100, cy=0,    r=0)
    circle.add_key_frame(2, cx=0,    cy=-100, r=40)
    circle.add_key_frame(4, cx=100,  cy=0,    r=0)
    circle.add_key_frame(6, cx=0,    cy=100,  r=40)
    circle.add_key_frame(8, cx=-100, cy=0,    r=0)
    d.append(circle)
    r = dw.Rectangle(0, 0, 0, 0, fill='silver')  # Moving square
    r.add_key_frame(0, x=-100, y=0,       width=0,  height=0)
    r.add_key_frame(2, x=0-20, y=-100-20, width=40, height=40)
    r.add_key_frame(4, x=100,  y=0,       width=0,  height=0)
    r.add_key_frame(6, x=0-20, y=100-20,  width=40, height=40)
    r.add_key_frame(8, x=-100, y=0,       width=0,  height=0)
    d.append(r)

    # Changing text
    dw.native_animation.animate_text_sequence(
            d,
            [0, 2, 4, 6],
            ['0', '1', '2', '3'],
            30, 0, 1, fill='yellow', center=True)

    html(d.as_html(), width=420, height=320)

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
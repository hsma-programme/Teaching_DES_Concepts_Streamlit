'''
A Streamlit application based on Monks and 

Allows users to interact with an increasingly more complex treatment simulation 
'''
import streamlit as st

from helper_functions import read_file_contents, add_logo, mermaid
from model_classes import *
# from st_pages import show_pages_from_config, add_page_title

st.set_page_config(
     page_title="The Code",
     layout="wide",
     initial_sidebar_state="expanded",
 )

# add_page_title()

# show_pages_from_config()

add_logo()

with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

## We add in a title for our web app's page
st.title("Discrete Event Simulation Playground")
st.subheader("What's going on under the hood?")

gc.collect()

# Code from the intro to simpy session run in HSMA 5
# https://github.com/hsma-programme/3a_introduction_to_discrete_event_simulation/blob/main/3A_Introduction_to_Discrete_Event_Simulation/Lecture_Examples/simple_simpy.py
# TODO: Maybe change the env.now statements to be print instead
# TODO: Go back through explanations and see where we can simplify them. 

st.markdown(
    """
    If you join us on the HSMA course, you will learn how to write models just like this one using the Python programming language and the SimPy package.

And actually, to create a basic model, we don't need all that much code.


# Import packages

We start by importing two packages. These are online files of pre-written code that will do a lot of the repetitive or complex tasks for us.
"""
)

st.code(
"""
import simpy
import random
""",
   language='python' 
)

"""
Next, we need to define something that will generate our patients
"""

st.code(
"""
def patient_generator(env, wl_inter, mean_consult, nurse):
    p_id = 0 # We'll set this up to give each patient created a unique ID

    # Keep doing this indefinitely (whilst the program's running)
    while True:        
        # Create an instance of the activity generator function (defined below) which will define what happens to our patients.
        wp = activity_generator(
            env, # let it make use of our simulated world
            mean_consult, # tell it how long a consultion takes on average
            nurse,  # tell it which nurse it's going to use
            p_id # tell it which patient it relates to
            )
        
        # Tell the simulation environment to actually process the person we've just created
        env.process(wp)
        
        # Calculate the time until the next patient arrives
        # Here we sample from an exponential distribution to determine how long that wait will be
        t = random.expovariate(1.0 / wl_inter)
        
        # Tell the simulation to freeze this function in place until that sampled inter-arrival time has elapsed
        yield env.timeout(t)
        
        # When the time has elapsed, and we're ready for the next patient to arrive, this generator function will resume from here.  
        
        # Now, we add one to the patient ID so the next person has a unique ID, and do it all again!
        p_id += 1
""",
   language='python' 
)

"""
Next we need to define something that will actually do something to those patients!
"""

st.code(
"""
def activity_generator(env, mean_consult, nurse, p_id):
    
    # Use 'env.now' to make a note of the time the person turned up
    time_entered_queue_for_nurse = env.now

    # We now call the request() function of the Nurse resource so that we can 
    # grab a nurse that is available and get them to do the patient's treatment

    # We use a 'with' statement to indicate that all of the code in the indented block needs to be done with the nurse resource, after which it can release it
    with nurse.request() as req:
    # The first thing we do with the request is call a yield on it.  
    # This means everything relating to this patient will freezes in place until a nurse is available - but anything else happening in the simulation will keep ticking along
    yield req

    # Once a nurse is available it'll resume from here, so when we get to this point we know a nurse is now available, and the patient has finished queuing.  
    # Now we can record the current simulation time (which can help us work out how long the patient was queuing)

    time_left_queue_for_nurse = env.now

    time_in_queue_for_nurse = (time_left_queue_for_nurse -
                                time_entered_queue_for_nurse)

    # Now the patient is with the nurse, we need to calculate how long they spend in their consultation.  

    # Here, we'll randomly sample from an exponential distribution with the mean consultation time we passed into the function.
    sampled_consultation_time = random.expovariate(1.0 / mean_consult)

    # Tell the simulation to freeze this function in place until that sampled consultation time has elapsed (which is also keeping the nurse in use and unavailable elsewhere, as we're still in the 'with' statement)
    yield env.timeout(sampled_consultation_time)

    # Once we get here, then control has been passed back to this instance of the generator function, as so we know that the activity time we sampled above has now elapsed.

    # Let's make a note of when the patient leaves the consultation.
    time_consultation_ended = env.now
""",
   language='python' 
)

"""
Now we have generated two things:
- something that will genreate new patients for the unit
- something that will process the patients 

So our next step is just to create a virtual world for our simulation to take place in.
"""

st.code(
"""
env = simpy.Environment()
""",
   language='python' 
)

"""
Next, we create one nurse inside our virtual world.
"""

st.code(
"""
nurse = simpy.Resource(env, capacity=1)
""",
   language='python' 
)

"""
Then we tell our virtual world to start making patients!
"""

st.code(
   """
env.process(patient_generator(
    env, # Tell it to use our virtual world
    wl_inter, # Tell it the average time between patients arriving
    mean_consult, # Tell it the average time between patients
    nurse # Tell it to use the nurse we created
    )
    """,
   language='python' 
)

"""
Finally, we tell it to run the simulation for a certain number of minutes: in this case, let's go for 10 hours.
"""

st.code(
   """
    env.run(until=600)
   """,
   language='python' 
)

"""
And that's it! This is all the code you need to make your very first simulation model. 
"""


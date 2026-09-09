'''
A page containing information about

---

A Streamlit application based on the open treatment centre simulation model from Monks.T, Harper.A, Anagnoustou. A, Allen.M, Taylor.S. (2022)

Original Model: https://github.com/TomMonks/treatment-centre-sim/tree/main

Allows users to interact with an increasingly complex treatment centre simulation
'''
import gc
import streamlit as st

from helper_functions import add_logo

st.set_page_config(
     page_title="Find Out More",
     layout="wide",
     initial_sidebar_state="expanded",
 )

add_logo()

with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

## We add in a title for our web app's page
st.title("Discrete Event Simulation Playground")

st.subheader("Simulation Modelling in the HSMA Programme")

gc.collect()

st.markdown(
    """
    Tthe HSMA programme contains
    - three sessions on discrete event simulation (the technique used in this web app)
    - a session on system dynamics modelling (for large, system-scale problems)
    - sessions on agent-based simulation (for modelling interactions and motivations of individuals that lead to high-level patterns, e.g. to look at the spread of disease)
    - sessions on creating web-based interfaces (like this one!) for allowing users to interact with your models
    """
)

st.divider()

st.subheader("Where Can I Find Out More?")

st.markdown(
    """
    If you just can't wait until the next round of HSMA, you can access the previous content on discrete event simulation below.

    However - if you apply to HSMA, you will get the benefit of support from the HSMA team as well as a peer support group.

    Take a look at our full DES module page on our website [here](https://hsma.co.uk/hsma_content/modules/current_module_details/2_des.html).
    """
)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("An Introduction to DES Concepts")
    st.video("https://www.youtube.com/watch?v=TxdvJQxuSx4")

with col2:
    st.subheader("Starting to code DES models with Simpy")
    st.video("https://www.youtube.com/watch?v=nHgyJ6i0TGs")

with col3:
    st.subheader("Coding More Complex Videos in Simpy")
    st.video("https://www.youtube.com/watch?v=FBVBKtVkayA")


st.divider()

st.header("The DES Book")

book_text_col, book_blank_col_1, book_image_col, book_blank_col_2 = st.columns([0.6, 0.1, 0.2, 0.1])

with book_image_col:
    st.image("https://raw.githubusercontent.com/hsma-programme/Teaching_DES_Concepts_Streamlit/refs/heads/main/resources/des_cover_image.jpeg")



with book_text_col:
    st.markdown("""
    There's so much to teach you about DES that we just couldn't fit it all into our sessions - so we wrote a book!

    You can read it at [des.hsma.co.uk](https://des.hsma.co.uk)

    The DES book is a free eBook that takes you from your first models through to much more complex modelling concepts than we cover in the taught sessions.

    We'd love to [hear from you](mailto:info@hsma.co.uk) if you find the book useful, or if there are additional concepts you would like it to cover.
    """)

    st.divider()

    st.header("HSMA DES Projects")

    st.markdown(
        """
        Several HSMA projects have made use of discrete event simulation to motivate incredible changes in health systems.

        You can view some of them on our [projects page](https://hsma.co.uk/previous_projects/projects_by_methods.html#discrete-event-simulation)
        """
    )

st.divider()

st.header("Building Web Apps Like This One")

st.markdown(
    """

    Finally, this whole exercise website has been written in Streamlit - another topic we cover on the course!
    Streamlit allows you to create highly customisable websites that allow you to share results with users and give them the freedom to interact with powerful Python code without needing Python on their own computers.

    You can view our streamlit training [here](https://hsma.co.uk/hsma_content/modules/current_module_details/7_git_and_web_development.html)

    Session 7B gets you started on writing Streamlit apps, and 7C helps you to build and deploy a discrete event simulation front-end just like this one!
    """
)

st.divider()

st.subheader("Where Can I Find the Code for this Model?")

st.markdown("All of the code used to make this model, the visualisation and the streamlit app can be found in [this GitHub repository](https://github.com/hsma-programme/Teaching_DES_Concepts_Streamlit).")

st.markdown("The code is available under the MIT licence so may be freely used and adapted - though we'd love to [hear about it](mailto:info@hsma.co.uk) if you do use the app or code!")

st.markdown("If you want to create an animated visualisation like the ones used here, check out the [vidigi](https://bergam0t.github.io/vidigi/vidigi_docs/) package")

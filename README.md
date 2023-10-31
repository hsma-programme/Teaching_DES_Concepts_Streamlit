This is a Streamlit application designed to walk people new to discrete event simulation through the key concepts.

It will allow them to get comfortable with the idea of sampling frm distributions, simulation replications, arrival generation, branching paths, and optimising systems. 


# Instructions to run
The app will be publically deployed on the Streamlit community platform once the first version is complete. 

Until then
1. Clone the repository.
2. Navigate to the folder location on your machine via a terminal/command line. 
3. Create a virtual environment using the requirements.txt file.
4. Activate the virtual environment.
4. Ensuring you are in the same folder as `Introduction.py``, run the command `python streamlit run Introduction.py`

# Model info

This model uses a modified version of the open treatment centre simulation model from Monks.T, Harper.A, Anagnoustou. A, Allen.M, Taylor.S. (2022)
!(Link)[https://github.com/TomMonks/treatment-centre-sim/tree/main]

Due to an oversight it was not forked directly from this repository. 

# Developer info - app design

This is a multipage streamlit app. The landing page (Introduction.py) is in the root folder, but all subsequent pages are in the 'pages' subfolder.

Key model functions are in
- distribution_classes.py
- helper_functions.py

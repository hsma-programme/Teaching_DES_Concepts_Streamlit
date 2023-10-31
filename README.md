**Work in progress**

This is a Streamlit application designed to walk people new to discrete event simulation through the key concepts.
It will be used at the open day for the HSMA 6 programme. 

It will allow them to get comfortable with the idea of sampling frm distributions, simulation replications, arrival generation, branching paths, and optimising systems. 

# What is HSMA?

HSMA is a course for people in England working in the health, social care and policing organisations. Over 15 months it trains participants in operational research and data science techniques to aid with service development and decision making. 

More information about the course can be found [here](https://sites.google.com/nihr.ac.uk/hsma)

All of the course materials are open source - check out [our repositories](https://github.com/hsma-programme)  

# Instructions to run
The app will be publically deployed on the Streamlit community platform once the first version is complete. 

Until then
1. Clone the repository.
2. Navigate to the folder location on your machine via a terminal/command line. 
3. Create a virtual environment using the requirements.txt file.
4. Activate the virtual environment.
4. Ensuring you are in the same folder as `Introduction.py`, run the command `python streamlit run Introduction.py`

# Model info

This model uses a modified version of the open treatment centre simulation model from Monks.T, Harper.A, Anagnoustou. A, Allen.M, Taylor.S. (2022)

[Link to treatment centre simulation repository](https://github.com/TomMonks/treatment-centre-sim/tree/main)

Due to an oversight it was not forked directly from this repository. 

# Developer info - app design

This is a multipage streamlit app. The landing page (Introduction.py) is in the root folder, but all subsequent pages are in the 'pages' subfolder.

Key model functions are in
- distribution_classes.py
- helper_functions.py

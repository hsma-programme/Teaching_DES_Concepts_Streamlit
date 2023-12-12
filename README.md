**Work in progress - under active development**

This is a Streamlit application designed to walk people new to discrete event simulation through the key concepts.
It will be used at the open day for the HSMA 6 programme. 

It will allow them to get comfortable with the idea of
- sampling from distributions
- simulation replications
- arrival generation
- generating and using resources
- branching paths
- optimising systems

A version of the final model can also be loaded in Google Colab.
<a target="_blank" href="https://colab.research.google.com/github/hsma-programme/Teaching_DES_Concepts_Streamlit/blob/main/nb_4_full_model.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>

![image](https://github.com/hsma-programme/Teaching_DES_Concepts_Streamlit/assets/29951987/c55e132d-77b6-43f6-bc98-09434b87709b)

An animated visual representation of the event log has also been generated using Plotly, allowing users to follow individuals through a simulation and quickly see where queues are building up in the system.

https://github.com/hsma-programme/Teaching_DES_Concepts_Streamlit/assets/29951987/1adc36a0-7bc0-4808-8d71-2d253a855b31

Outputs can be compared across multiple scenarios within a single user session. 

![image](https://github.com/hsma-programme/Teaching_DES_Concepts_Streamlit/assets/29951987/891e02bd-5b0e-4906-af81-c413f26182c3)

# What is HSMA?

HSMA is a course for people in England working in the health, social care and policing organisations. Over 15 months it trains participants in operational research and data science techniques to aid with service development and decision making. 

More information about the course can be found [here](https://sites.google.com/nihr.ac.uk/hsma)

All of the course materials are open source - check out [our repositories](https://github.com/hsma-programme)  

# Instructions to run
The app has can be accessed via the [Github Pages site](https://hsma-programme.github.io/Teaching_DES_Concepts_Streamlit/) 
Note that the page has been tested and confirmed working in Chrome, Edge and Safari. It does NOT work in Firefox due to issues with initiating the loading of the stlite dependencies.

Due to changes that have been made to ensure that the app works well when deployed via stlite, it is not possible to clone the repository and run it locally without first removing all instances where the `await` command has been used. 

However, it is possible to clone the repository and instead run it using the stlite preview extension for VSCode, which can be downloaded [here](https://marketplace.visualstudio.com/items?itemName=whitphx.vscode-stlite)
Note that you will need to restart VSCode after installing this extension.
Use CTRL+SHIFT+P in VSCode to launch the command pallete, then choose "Launch stlite preview". 
You then need to select Introduction.py from the drop-down that appears. 
The app should then launch in a preview pane within vscode, allowing you to make changes without deploying to github.

# Model info

This model uses a modified version of the open treatment centre simulation model from Monks.T, Harper.A, Anagnoustou. A, Allen.M, Taylor.S. (2022)

[Link to treatment centre simulation repository](https://github.com/TomMonks/treatment-centre-sim/tree/main)

All simulation logic uses the Simpy package.

# Developer info - app design

This is a multipage streamlit app. The landing page (Introduction.py) is in the root folder, but all subsequent pages are in the 'pages' subfolder.
HOWEVER - Introduction.py is not referenced directly in the stlite implementation when deployed on Github pages. Instead, code in Introduction.py needs to be manually synced to index.html.
All other pages will reflect exactly what is in the .py files within the pages subfolder - Introduction.py is the only exception to this rule.

The index.html controls the navigation of the pages within stlite, making the required pages, scripts and other resources available to pyodide by temporarily mounting them on a virtual filesystem on page load.

Key model functions are in
- distribution_classes.py
- model_classes.py

Additional functions are in
- helper_functions.py

Animation functions are in
- output_animation_functions.py


## Why stlite?

This app has been designed for use in workshops, meaning that high concurrent load is expected. Due to the relatively high computational load and large datasets expected, this would be likely to quickly overwhelm the free tier available via Streamlit Community. 
[Stlite](https://github.com/whitphx/stlite) is a port of Streamlit to WebAssembly, and uses [pyodide](https://pyodide.org/en/stable/), an implementation of python in the browser, meaning all computation is transferred over to the users computers without requiring them to install Python or any packages. To the end user, it will be indistinguishable from a normal web application - apart from the longer initial loading time. 

It should be noted that the performance of the app is highly dependent on the device the user is running it on, and the default model run length and number of runs has been deliberately set quite low to allow for maximum compatability, though load times on less powerful devices will be significantly longer and it may struggle to store multiple simulation replications. 

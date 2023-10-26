import urllib.request as request
import streamlit as st

def read_file_contents(file_name):
    ''''
    Read the contents of a file.

    Params:
    ------
    file_name: str
        Path to file.

    Returns:
    -------
    str
    '''
    with open(file_name) as f:
        return f.read()
    

def read_file_contents_web(path):
    """
    Download the content of a file from the GitHub Repo and return as a utf-8 string

    Notes:
    -------
        adapted from 'https://github.com/streamlit/demo-self-driving'

    Parameters:
    ----------
    path: str
        e.g. file_name.md

    Returns:
    --------
    utf-8 str

    """
    response = request.urlopen(path)
    return response.read().decode("utf-8")

def add_logo():
    '''
    Add a logo at the top of the page navigation sidebar

    Approach written by blackary on
    https://discuss.streamlit.io/t/put-logo-and-title-above-on-top-of-page-navigation-in-sidebar-of-multipage-app/28213/5
    
    '''
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://raw.githubusercontent.com/Bergam0t/Teaching_DES_Concepts_Streamlit/main/resources/hsma_logo.png);
                background-repeat: no-repeat;
                padding-top: 150px;
                background-position: 70px 30px;
            }
            [data-testid="stSidebarNav"]::before {
                content: "The DES Playground";
                padding-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 100px;
            }

        </style>
        """,
        unsafe_allow_html=True,
    )
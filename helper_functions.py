import urllib.request as request

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

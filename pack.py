from stlitepack import pack

pack(
    app_file="streamlit_app.py",
    extra_files_to_embed=[
        ".streamlit/config.toml",
    ],
    prepend_github_path="hsma-programme/des_playground_minimal",
    extra_files_to_link=[
        "styles.css",
        "resources/hsma_logo.png",
        "resources/hsma_logo_transparent_background_large.png",
        "resources/hsma_logo_transparent_background_small.png",
        "model_classes.py",
        "distributions.py",
        "helper_functions.py",
        "data/ed_arrivals.csv",
    ],
    run_preview_server=True,
    requirements=[
        # Pin plotly explicitly and ahead of vidigi: vidigi allows
        # plotly<7,>=5.12, and micropip's resolver lands on the newest (6.9.x,
        # "Metadata-Version: 2.4") which it then can't use and won't backtrack
        # from, reporting the whole range as having "no pure Python 3 wheel".
        # 6.0.1 ("Metadata-Version: 2.2") has only bundled deps (narwhals,
        # packaging) in Pyodide 0.29.3.
        "plotly==6.0.1",
        "vidigi<2.0.0",
        "simpy",
    ],
    stylesheet_version="1.8.1",
    js_bundle_version="1.8.1",
)

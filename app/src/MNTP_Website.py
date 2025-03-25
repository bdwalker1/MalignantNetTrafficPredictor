import os
import requests

from fastapi.responses import HTMLResponse

def html_page( title: str, content: str ):
    html_output = F"""
    <html>
    <head>
    {style_shaeet()}
    <link rel="stylesheet" href="/mntp/webpage/mntp.css">
    <title>{title}</title>
    </head>
    <body>
    <h1>{title}</h1>
    <p>{content}</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_output, status_code=200)

def landing_page():
    page_content = f"""
         <h3>This web page serves as a demonstration of how go use the Malignant Net Traffic Predictor API.</h3><br>
         <a href="/docs/">Go to the /docs/ page</a><br>
         {make_model_list()}
         
    """
    return html_page("Malignant Network Traffic Predictor", page_content)

def style_shaeet():
    strCSS = "<style>"
    filecss = open("/mntp/webpage/mntp.css", "r+t")
    strCSS += filecss.read()
    filecss.close()
    strCSS += "</style>"
    return strCSS

def make_model_list():
    # models = requests.post("http://127.0.0.1:8000/listmodels/", headers={"accept": "application/json"}, data={}).json()
    strModelList = "<br>Available models:<br><select name='model'>"
    from src.MalignantNetTrafficPredictor import MalignantNetTrafficPredictor
    mntp = MalignantNetTrafficPredictor()
    models = mntp.list_available_models()
    model_names = sorted(models.keys())
    for name in model_names:
        strModelList += f"<option value=\"{models[name]["type"]}|{models[name]["filename"]}\">{name} - {models[name]["desc"]}</option>"
    strModelList += "</select>"
    return strModelList

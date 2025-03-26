import os
import requests
import json
from fastapi.responses import HTMLResponse

__api_url = "http://mntp-api.hopto.me"

def html_page( title: str, content: str ):
    html_output = F"""
    <html>
    <script src="/static/demo_page.js" type="text/javascript" defer></script>
    <head>
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
    {style_shaeet()}
    <title>{title}</title>
    </head>
    <body>
    <h1>{title}</h1>
    <p>{content}</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_output, status_code=200)

def landing_page(api_url: str):
    global __api_url
    __api_url = api_url
    page_content = f"""
         <h3>This web page serves as a demonstration of how to use the Malignant Net Traffic Predictor API.</h3><br>
         {show_loaded_model()}
         {make_model_list()}
         {model_creator()}
         <br>
         <hr>
         <a href="{__api_url}/docs/">Go to the Fast API /docs/ page</a><br>
         
    """
    return html_page("Malignant Network Traffic Predictor", page_content)

def style_shaeet():
    strCSS = "<style>"
    filecss = open("./webpage/demo_page.css", "r+t")
    strCSS += filecss.read()
    filecss.close()
    strCSS += "</style>"
    return strCSS

def show_loaded_model():
    global __api_url
    str_output = "<p><span style=\"font-size: 1.25rem; font-weight: bold;\">Loaded Model:</span><br>"
    model = requests.post(__api_url + "/loadedmodel/", headers={"accept": "application/json"}, data={})
    model_dict = json.loads(model.json())
    str_output += "<table>"
    str_output += table_row(["<b>Name:</b>", model_dict['name']])
    str_output += table_row(["<b>Description:</b>", model_dict['desc']])
    str_output += "</table><br>"
    return str_output

def make_model_list():
    global __api_url
    str_models = ("<p><span style=\"font-size: 1.25rem; font-weight: bold;\">"
                    "Models available in this API container:</span><br>"
                    "<table>")
    str_models += table_row(["Name", "Type", "Description", "Actions"], header=True)
    models = requests.post(__api_url + "/listmodels/", headers={"accept": "application/json"}, data={})
    models_dict = json.loads(models.json())
    model_names = sorted(list(models_dict.keys()))
    for model_name in model_names:
        lst_model = [model_name]
        lst_model.append(models_dict[model_name]["type"])
        lst_model.append(models_dict[model_name]["desc"])
        actions = ("<button type=\"button\" onclick='loadmodel(\"" + __api_url + "\", \""
                   + models_dict[model_name]["type"] +"\", \""
                   + models_dict[model_name]["filename"] + "\");'>Load</button>\n")
        if models_dict[model_name]["type"] == "user":
            actions += ("<br><button type=\"button\" onclick='deletemodel(\"" + __api_url + "\", \""
                       + models_dict[model_name]["filename"] + "\");'>Delete</button>\n")
        lst_model.append(actions)
        str_models += table_row(lst_model)
    str_models += "</table>"
    return str_models

def model_creator():
    global __api_url
    str_creator = ("<p><span style=\"font-size: 1.25rem; font-weight: bold;\">"
                    "Create a New Model:</span><br>")
    str_creator += "<form id='form_create_model' action='javascript:;' onsubmit='model_creator(\"" + __api_url + "\",this);' >"
    str_creator += "<label for='name'>Name: </label><input type='text' name='name' value='' size=36 maxlength=30 /><br>"
    str_creator += "<label for='description'>Description: </label><input type='text' name='description' value='' size=64 maxlength=60 /><br>"
    str_creator += "<label for='n_estimators'>Estimators: </label><input type='number' name='n_estimators' value='1' size=3 min=1 max=20 /><br>"
    str_creator += "<label for='learning_rate'>Learning Rate: </label><input type='number' name='learning_rate' value='1.0' size=3 min=0.1 max=1.5 step=0.1 /><br>"
    str_creator += "<label for='max_depth'>Max Depth: </label><input type='number' name='max_depth' value='1' size=3 min=1 max=15 /><br>"
    str_creator += "<label for='trainingdataurl'>Training file URL: </label><input type='url' name='trainingdataurl' value='https://github.com/bdwalker1/UCSD_MLE_Bootcamp_Capstone/raw/refs/heads/master/data/MalwareDetectionInNetworkTrafficData/training/NTAMalignantTrafficPredictor_Training.csv?download=' size=150 maxlength=200 /><br>"
    str_creator += "<input type='submit' value='Make Model' />"
    str_creator += "</form><br>"
    return str_creator

def table_row(items, header=False):
    if header:
        cell_tag = "th"
    else:
        cell_tag = "td"
    str_output = "<tr>"
    for item in items:
        str_output += f"<{cell_tag}>{item}</{cell_tag}>"
    str_output += "</tr>"
    return str_output
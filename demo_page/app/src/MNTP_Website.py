import os
import requests
import json
from fastapi.responses import HTMLResponse

__api_url = ""

def html_page( title: str, content: str ):
    html_output = F"""
    <html>
    <script src="/static/demo_page.js" type="text/javascript" defer></script>
    <script type="text/javascript">
    function sayhi() {{ alert("Hi"); }}
</script>
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

def landing_page(base_url: str):
    global __api_url
    __api_url = str(base_url).removesuffix("/") + ":8000"
    page_content = f"""
         <h3>This web page serves as a demonstration of how to use the Malignant Net Traffic Predictor API.</h3><br>
         {show_loaded_model()}
         {make_model_list()}
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
    str_output = "<p><span style=\"font-size: 1.25rem; font-weight: bold;\">Loaded Model:</span><br>"
    model = requests.post("http://127.0.0.1:8000/loadedmodel/", headers={"accept": "application/json"}, data={})
    model_dict = json.loads(model.json())
    str_output += "<table>"
    str_output += table_row(["<b>Name:</b>", model_dict['name']])
    str_output += table_row(["<b>Description:</b>", model_dict['desc']])
    str_output += "</table><br>"
    return str_output

def make_model_list():
    str_models = ("<p><span style=\"font-size: 1.25rem; font-weight: bold;\">"
                    "Models available in this API container:</span><br>"
                    "<table>")
    str_models += table_row(["Name", "Type", "Description", "Actions"], header=True)
    models = requests.post("http://127.0.0.1:8000/listmodels/", headers={"accept": "application/json"}, data={})
    models_dict = json.loads(models.json())
    model_names = sorted(list(models_dict.keys()))
    for model_name in model_names:
        lst_model = [model_name]
        lst_model.append(models_dict[model_name]["type"])
        lst_model.append(models_dict[model_name]["desc"])
        actions = ("<a onclick='loadmodel(\"" + __api_url + "\", \""
                   + models_dict[model_name]["type"] +"\", \""
                   + models_dict[model_name]["filename"] + "\");'>Load</a>\n")
        lst_model.append(actions)
        str_models += table_row(lst_model)
    str_models += "</table>"
    return str_models

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
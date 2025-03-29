import requests
import json
from fastapi.responses import HTMLResponse
import src.appvars as appvars
from src.appvars import is_uuid
from uuid import UUID

def html_page( title: str, content: str ):
    html_output = F"""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <link rel="icon" type="image/x-icon" href="/static/favicon.ico" />
            <link rel="stylesheet" href="/static/demo_page.css" type="text/css" />
            <script src="/static/demo_page.js" type="text/javascript" defer></script>
            <title>{title}</title>
        </head>
        <body>
            {content}
        </body>
    </html>
    """
    return HTMLResponse(content=html_output, status_code=200)

async def landing_page(session_id: UUID, session_data: appvars.SessionData):
    title = "Malignant Network Traffic Predictor"
    page_content = f"""
        <img src="/static/mntp_icon.png" alt="{title} Icon" class="logo" />
        <h3>&nbsp;<br></h3>
        <h1>{title}</h1>
        <h3>This web page serves as a demonstration of how to use the Malignant Net Traffic Predictor API.</h3><br>
        {await show_loaded_model(session_id)}
        <div class="container">
            <!-- Left Column with Tabs -->
            <div class="tab-column">
                <button class="tab-button active" onclick="openTab('tab1')">Manage Models</button>
                <button class="tab-button" onclick="openTab('tab2')">Create a Model</button>
                <button class="tab-button" onclick="openTab('tab3')">Predict From JSON</button>
                <button class="tab-button" onclick="openTab('tab4')">Predict From File</button>
                <button class="tab-button" onclick="openTab('tab5')">Predict File to File</button>
            </div>
            
            <!-- Right Content Area -->
            <div class="content-section">
                <!-- Tab 1 Content -->
                <div id="tab1" class="tab-content active">
                    {await make_model_list(session_id)}
                </div>
                <!-- Tab 2 Content -->
                <div id="tab2" class="tab-content">
                    {model_creator()}
                </div>
                <!-- Tab 3 Content -->
                <div id="tab3" class="tab-content">
                    {predict_from_json()}
                </div>
                <!-- Tab 4 Content -->
                <div id="tab4" class="tab-content">
                    {predict_from_file()}
                </div>
                <!-- Tab 5 Content -->
                <div id="tab5" class="tab-content">
                    {predict_file2file()}
                </div>
            </div>
        </div>
        <hr>
        Go to the <a href="{appvars.api_url}/docs/">Fast API /docs/ page</a> to interact directly with the API.<br>
        <div class="secret" id="session_id">{str(session_id)}</div>
        <div class="secret" id="api_session_id">{str(session_data.api_session_id)}</div>
        
    """
    return html_page(title, page_content)

async def show_loaded_model(session_id: UUID):
    session_id, session_data, is_new_session = appvars.get_session_data(session_id)
    str_output = "<div class=\"loadedmodel\"><h2>Loaded Model</h2>"
    headers = {
        "accept": "application/json",
    }
    qstring = ""
    if is_uuid(session_data.api_session_id):
        headers["session_id"] = F"{session_data.api_session_id}"
        qstring = F"session_id={session_data.api_session_id}"
    model = requests.post(appvars.api_url + F"/loadedmodel/?{qstring}", headers=headers, data={})
    if model.headers.get('session_id') != session_data.api_session_id:
        session_data.api_session_id = model.headers.get('session_id')
        appvars.update_session_data(session_id, session_data)
    model_dict = json.loads(model.json())
    str_output += "<table>"
    str_output += table_row(["<b>Name</b>", model_dict['name']])
    str_output += table_row(["<b>Description</b>", model_dict['desc']])
    str_output += "</table></div>"
    return str_output

async def make_model_list(session_id: UUID):
    session_id, session_data, is_new_session = appvars.get_session_data(session_id)
    str_models = ("<div id=\"model_list\"><h2>Models available in this API container</h2>"
                    "<table>")
    str_models += table_row(["Name", "Type", "Description", "Actions"], header=True)
    headers = {
        "accept": "application/json",
    }
    qstring = ""
    if is_uuid(session_data.api_session_id):
        headers["session_id"] = F"{session_data.api_session_id}"
        qstring = F"session_id={session_data.api_session_id}"
    models = requests.post(appvars.api_url + F"/listmodels/?{qstring}", headers=headers, data={})
    if models.headers.get('session_id') != session_data.api_session_id:
        session_data.api_session_id = models.headers.get('session_id')
        appvars.update_session_data(session_id, session_data)
    models_dict = json.loads(models.json())
    model_names = sorted(list(models_dict.keys()))
    for model_name in model_names:
        lst_model = [model_name, models_dict[model_name]["type"], models_dict[model_name]["desc"]]
        actions = (F"<button type=\"button\" onclick='loadmodel(\"{models_dict[model_name]["type"]}\", "
                   F"\"{models_dict[model_name]["filename"]}\");'>Load</button>\n")
        if models_dict[model_name]["type"] == "user":
            actions += (F"<br><button type=\"button\" onclick='deletemodel(\""
                        F"{models_dict[model_name]["filename"]}\");'>Delete</button>\n")
        lst_model.append(actions)
        str_models += table_row(lst_model)
    str_models += "</table></div>"
    return str_models

def model_creator():
    str_creator = ("<div id=\"model_creator\"><span style=\"font-size: 1.25rem; font-weight: bold;\">"
                    "Create a New Model:</span><br>")
    str_creator += "<form id='form_create_model' action='javascript:;' onsubmit='model_creator(this);' >"
    str_creator += "<label for='name'>Name: </label><input type='text' name='name' value='' size=36 maxlength=30 /><br>"
    str_creator += "<label for='description'>Description: </label><input type='text' name='description' value='' size=64 maxlength=60 /><br>"
    str_creator += "<label for='n_estimators'>Estimators: </label><input type='number' name='n_estimators' value='1' size=3 min=1 max=20 /><br>"
    str_creator += "<label for='learning_rate'>Learning Rate: </label><input type='number' name='learning_rate' value='1.0' size=3 min=0.1 max=1.5 step=0.1 /><br>"
    str_creator += "<label for='max_depth'>Max Depth: </label><input type='number' name='max_depth' value='1' size=3 min=1 max=15 /><br>"
    str_creator += ("<label for='trainingdataurl'>Training file URL: </label><input type='url' name='trainingdataurl' "
                    "value='https://github.com/bdwalker1/MalignantNetTrafficPredictor_Data/raw/refs/heads/main/training/MalignantNetTrafficPredictor_Training.csv?download='"
                    " size=150 maxlength=200 /><br>")
    str_creator += "<input type='submit' value='Make Model' />"
    str_creator += "</form><br></div>"
    return str_creator

def predict_from_json():
    str_section = "<div id=\"predict_from_json\"><h2>Predict from JSON string:</h2><br>"
    str_section += "<form id='form_predict_from_json' action='javascript:;' onsubmit='predict_from_json(this);' >"
    str_section += "<label for='json_string'>JSON String: </label></br>"
    str_section += "<textarea id=\"json_string\" name=\"json_string\" rows=\"10\" cols=\"80\">"
    str_section += """
{
	"ts": {
		"0": 1532540299.0008280277,
		"1": 1569018359.1118040085,
		"2": 1532530169.9988269806,
		"3": 1532559589.0070989132,
		"4": 1545427458.8178169727,
		"5": 1532541264.9982740879,
		"6": 1545473184.5008220673,
		"7": 1532584048.0054368973,
		"8": 1545408894.0408430099,
		"9": 1545415782.5179030895,
		"10": 1545473205.8314321041
	},
	"uid": {
		"0": "CuJz9l20s9QJ7C46wf",
		"1": "Cv5fgf2vlLuylYXpv1",
		"2": "CQPvIC4KSsR6gji5Gk",
		"3": "CqifsFRh08VZm3sCl",
		"4": "CXBoSb1a1YmtikRf84",
		"5": "CPkeOFVf9X0v6VZRa",
		"6": "CyBVT52L5iAVfXkgrk",
		"7": "CLKO0C1hoyhty82Lgc",
		"8": "CGlLp43Fr3pBsrWpt7",
		"9": "C4XOhleVElYWlMoX8",
		"10": "CBGxQp3uBdx2ZoGiBj"
	},
	"id.orig_p": {
		"0": 64575,
		"1": 20137,
		"2": 58240,
		"3": 57194,
		"4": 53682,
		"5": 28586,
		"6": 50680,
		"7": 11169,
		"8": 35426,
		"9": 59524,
		"10": 27668
	},
	"id.resp_p": {
		"0": 23,
		"1": 62336,
		"2": 81,
		"3": 81,
		"4": 23,
		"5": 81,
		"6": 992,
		"7": 23,
		"8": 23,
		"9": 23,
		"10": 992
	},
	"proto": {
		"0": "tcp",
		"1": "tcp",
		"2": "tcp",
		"3": "tcp",
		"4": "tcp",
		"5": "tcp",
		"6": "tcp",
		"7": "tcp",
		"8": "tcp",
		"9": "tcp",
		"10": "tcp"
	},
	"service": {
		"0": "-",
		"1": "-",
		"2": "-",
		"3": "-",
		"4": "-",
		"5": "-",
		"6": "-",
		"7": "-",
		"8": "-",
		"9": "-",
		"10": "-"
	},
	"conn_state": {
		"0": "S0",
		"1": "OTH",
		"2": "S0",
		"3": "S0",
		"4": "S0",
		"5": "S0",
		"6": "RSTOS0",
		"7": "S0",
		"8": "S0",
		"9": "S0",
		"10": "RSTOS0"
	},
	"history": {
		"0": "S",
		"1": "C",
		"2": "S",
		"3": "S",
		"4": "S",
		"5": "S",
		"6": "I",
		"7": "S",
		"8": "S",
		"9": "S",
		"10": "I"
	},
	"orig_pkts": {
		"0": 1,
		"1": 0,
		"2": 1,
		"3": 1,
		"4": 3,
		"5": 1,
		"6": 3,
		"7": 1,
		"8": 1,
		"9": 1,
		"10": 3
	},
	"orig_ip_bytes": {
		"0": 40,
		"1": 0,
		"2": 40,
		"3": 40,
		"4": 180,
		"5": 40,
		"6": 120,
		"7": 40,
		"8": 60,
		"9": 60,
		"10": 120
	},
	"resp_pkts": {
		"0": 0,
		"1": 0,
		"2": 0,
		"3": 0,
		"4": 0,
		"5": 0,
		"6": 0,
		"7": 0,
		"8": 0,
		"9": 0,
		"10": 0
	},
	"resp_ip_bytes": {
		"0": 0,
		"1": 0,
		"2": 0,
		"3": 0,
		"4": 0,
		"5": 0,
		"6": 0,
		"7": 0,
		"8": 0,
		"9": 0,
		"10": 0
	}
}
    """
    str_section += "</textarea><br>"
    str_section += "<input type='submit' value='Get Predictions' />"
    str_section += "</form><br>"
    str_section += ("<iframe id=\"json_predictions\" name=\"json_predictions\" "
                    "class=\"results\" src=\"/blank\" ></iframe>")
    str_section += "</div>"
    return str_section

def predict_from_file():
    str_section = "<div id=\"predict_from_json\"><h2>Predict from input file:</h2><br>"
    str_section += "<form id='form_predict_from_file' action='javascript:;' onsubmit='predict_from_file(this);' >"
    str_section += ("<label for='inputdataurl'>Path/URL to input file:  (<b>Note:</b> File location must be accessible to the "
                    "machine/system the API is running on.)</label>")
    str_section += ("<input type='text' name='inputdataurl' "
                    "value='https://github.com/bdwalker1/MalignantNetTrafficPredictor_Data/raw/refs/heads/main/testing/MalignantNetTrafficPredictor_Testing.csv?download=' "
                    "size=150 maxlength=200 /><br>")
    str_section += "<input type='submit' value='Get Predictions' />"
    str_section += "</form><br>"
    str_section += ("<iframe id=\"file_predictions\" name=\"file_predictions\" "
                    "class=\"results\" src=\"/blank\" ></iframe>")
    str_section += "</div>"
    return str_section

def predict_file2file():
    str_section = "<div id=\"predict_file2file\"><h2>Predict from input file to output file:</h2><br>"
    str_section += "<form id='form_predict_file2file' action='javascript:;' onsubmit='predict_file2file(this);' >"
    str_section += ("<label for='inputdataurl'>Path/URL to input file: (<b>Note:</b> File location must be accessible to the "
                    "machine/system the API is running on.)</label>")
    str_section += ("<input type='text' name='inputdataurl' "
                    "value='https://github.com/bdwalker1/MalignantNetTrafficPredictor_Data/raw/refs/heads/main/testing/MalignantNetTrafficPredictor_Testing.csv?download=' "
                    "size=150 maxlength=200 /><br>")
    str_section += ("<label for='outputurl'>Path/URL to output file:  (<b>Note:</b> File location must be accessible to the "
                    "machine/system the API is running on.)</label>")
    str_section += "<input type='text' name='outputurl' value='/mntp-data/output/predictions.txt' size=150 maxlength=200 /><br>"
    str_section += "<input type='submit' value='Get Predictions' />"
    str_section += "</form><br>"
    str_section += ("<iframe id=\"file2file_results\" name=\"file2file_results\" "
                    "class=\"results\" src=\"/blank\" ></iframe>")
    str_section += "</div>"
    return str_section

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
import os, time
import re
import tempfile as __tempfile
from io import StringIO
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from uuid import UUID
import uvicorn
import pandas as pd
import src.appvars as appvars
from src.MalignantNetTrafficPredictor import MalignantNetTrafficPredictor

api = FastAPI()

net_predictor = MalignantNetTrafficPredictor()

appvars.init()

@api.get("/", name="API Demo Page", response_class=HTMLResponse)
async def root(session_id: UUID = None):
    session_id, session_data = appvars.get_session_data(session_id)
    headers = {"session_id": session_data.session_id}
    reply = HTMLResponse(F"Welcome to Malignant Net Traffic Predictor", headers=headers)
    return reply

@api.post("/listmodels/", name="List Available Models",
          description="List all the models currently available in the container.")
async def list_models(session_id: UUID = None):
    session_id, session_data = appvars.get_session_data(session_id)
    headers = {"session_id": session_data.session_id}
    dict_models = net_predictor.list_available_models()
    reply = JSONResponse(json.dumps(dict_models, indent=2), headers=headers)
    return reply

@api.post("/loadedmodel/", name="Show the Currently Loaded Model",
          description="Gets name and description of the currently loaded model.")
async def loaded_model(session_id: UUID = None):
    session_id, session_data = appvars.get_session_data(session_id)
    headers = {"session_id": session_data.session_id}
    if session_data.model_loaded == True:
        reply = JSONResponse(json.dumps({"name": session_data.model.model_name,
                                         "desc": session_data.model.model_description}, indent=2),
                             headers=headers)
    else:
        reply = JSONResponse(json.dumps({"name": "(no model loaded)", "desc": "(no model loaded)"}, indent=2),
                             headers=headers)
    return reply

@api.post("/getlatestmodel/", name="Get Latest Model", description="Get the latest model from the official GitHub repository.")
async def getlatestmodel(session_id: UUID = None):
    session_id, session_data = appvars.get_session_data(session_id)
    headers = {"session_id": session_data.session_id}
    try:
        model = net_predictor.retrieve_latest_model()
        session_data.model = model
        session_data.model_loaded = True
        appvars.update_session_data(session_id, session_data)
        print(F"Model name: {model.model_name}")
        print(F"Description: {model.model_description}")
        reply =  JSONResponse({"message": F"Retrieved model - Name: {model.model_name}; "
                                          F"Description: {model.model_description}"}, headers=headers)
    except Exception as e:
        reply = JSONResponse({"error": F"Failed to retrieve latest model. Ensure api container has access to "
                         F"https://github.com/bdwalker1/MalignantNetTrafficPredictor/raw/refs/heads/main/API/models/"
                         F". Details: {str(e)}"}, headers=headers)
    return reply

@api.post("/getmodelversion/", name="Get Specific Model Version", description="Get a specific model version from the official GitHub repository.")
async def get_modelversion(name: str, session_id: UUID = None):
    session_id, session_data = appvars.get_session_data(session_id)
    headers = {"session_id": session_data.session_id}
    try:
        model = net_predictor.retrieve_named_model(name)
        session_data.model = model
        session_data.model_loaded = True
        appvars.update_session_data(session_id, session_data)
        print(F"Model name: {model.model_name}")
        print(F"Description: {model.model_description}")
        reply =  JSONResponse({"message": F"Retrieved model - Name: {model.model_name}; "
                                          F"Description: {model.model_description}"}, headers=headers)
    except Exception as e:
        reply = JSONResponse({"error": F"Failed to retrieve model. Ensure model named '{name}' exists at "
                         F"https://github.com/bdwalker1/MalignantNetTrafficPredictor/raw/refs/heads/main/API/models/"
                         F"and that your api container has access to that site. Details: {str(e)}"}, headers=headers)
    return reply

@api.post("/savemodel/", name="Save Current Model", description="Save the current model to the user models folder.")
async def save_model(name: str, desc: str, filename: str, session_id: UUID = None):
    session_id, session_data = appvars.get_session_data(session_id)
    headers = {"session_id": session_data.session_id}
    if not session_data.model_loaded:
        reply = JSONResponse({"error": "You need have an active model before you can save."}, headers=headers)
    else:
        try:
            session_data.model["model"].save_model(name, desc, filename)
            reply = JSONResponse({"message": F"Saved model - Name: {name}; Description: {desc}"}, headers=headers)
        except Exception as e:
            reply = JSONResponse({"error": F"Failed to save model. {e}"}, headers=headers)
    return reply

@api.post("/deletemodel/", name="Delete a User-saved Model", description="Delete a user-saved model based on filename.")
async def delete_model(filename: str, session_id: UUID = None):
    session_id, session_data = appvars.get_session_data(session_id)
    headers = {"session_id": session_data.session_id}
    try:
        net_predictor.delete_model(filename)
        reply = JSONResponse({"message": F"Deleted user-saved model - Filename: {filename}"}, headers=headers)
    except Exception as e:
        reply = JSONResponse({"error": F"Failed to delete model file. {e}"}, headers=headers)
    return reply

@api.post("/loadofficialmodel/", name="Load Official Model", description="Load a model that has been downloaded from official repository.")
async def loadofficialmodel(filename: str, session_id: UUID = None):
    session_id, session_data = appvars.get_session_data(session_id)
    headers = {"session_id": session_data.session_id}
    try:
        model = net_predictor.load_official_model(filename)
        session_data.model = model
        session_data.model_loaded = True
        appvars.update_session_data(session_id, session_data)
        print(F"New active model loaded {model.model_name}")
        reply = JSONResponse({"message": F"Loaded model - Name: {model.model_name}; "
                                         F"Description: {model.model_description}"}, headers=headers)
    except Exception as e:
        reply = JSONResponse({"error": F"Failed to load model. {e}"}, headers=headers)
    return reply

@api.post("/loadusermodel/", name="Load a User-Saved Model", description="Load a specific user-saved model.")
async def loadusermodel(filename: str, session_id: UUID = None):
    session_id, session_data = appvars.get_session_data(session_id)
    headers = {"session_id": session_data.session_id}
    try:
        model = net_predictor.load_user_model(filename)
        session_data.model = model
        session_data.model_loaded = True
        appvars.update_session_data(session_id, session_data)
        print(F"New active model loaded {model.model_name}")
        reply = JSONResponse({"message": F"Loaded model - Name: {model.model_name}; "
                                         F"Description: {model.model_description}"}, headers=headers)
    except Exception as e:
        print(F"Failed to load model. {e}")
        reply = JSONResponse({"error": F"Failed to load model. {e}"}, headers=headers)
    return reply

@api.post("/predictfromjson/",
          name="Predict from JSON Text",
          description="Make predictions from a JSON text string.",
          response_class=JSONResponse)
async def predictfromjson(json_str: str, session_id: UUID = None):
    session_id, session_data = appvars.get_session_data(session_id)
    headers = {"session_id": session_data.session_id}
    if not session_data.model_loaded:
        reply = JSONResponse({"error": "You need have an active model before you can save."}, headers=headers)
    else:
        empty_df = pd.DataFrame([], columns=net_predictor.INPUT_FILE_COLS)
        try:
            input_df = pd.read_json(StringIO(json_str))
            columns_match = True
            for n, col in enumerate(input_df.columns):
                if col != empty_df.columns[n]:
                    columns_match = False
                    break
            if columns_match:
                for col in input_df.columns:
                    input_df[col] = input_df[col].astype(net_predictor.INPUT_FILE_COLS[col])
                predictor = session_data.model
                output_df = predictor.predict(input_df)
                print("Returning:" + str(output_df.to_json()))
                reply = JSONResponse(output_df.to_json(), headers=headers)
            else:
                reply = JSONResponse({"Error": "Columns do not match expected input schema."}, headers=headers)
        except Exception as e:
            reply = JSONResponse({"error": F"Exception occurred: {e}"}, headers=headers)
    return reply

@api.post("/predictfromfile/",
          name="Predict from Input File",
          description="Make predictions from an input file. The file path/url must be accessible to the API.")
async def predictfromfile(fileurl: str, session_id: UUID = None):
    session_id, session_data = appvars.get_session_data(session_id)
    headers = {"session_id": session_data.session_id}
    if not session_data.model_loaded:
        reply = JSONResponse({"error": "You need have an active model before you can save."}, headers=headers)
    else:
        try:
            predictor = session_data.model
            output_df = predictor.predictfromfile(fileurl)
            outputpath = maketempfile()
            output_df.to_csv(path_or_buf=outputpath, sep="|", lineterminator="\n", index=False)
            response = FileResponse(path=outputpath, filename="predictions.csv", media_type="application/csv", headers=headers)
            reply = response
        except Exception as e:
            reply = JSONResponse({"error": F"There was an error returning your results: {e}"}, headers=headers)
    return reply

@api.post("/predictfile2file/",
          name="Predict from Input File and Output to a File ",
          description=("Make predictions from an input file then save predictions to an output file. "
                      "Both the input and output file paths/urls must be accessible to the API."))
async def predictfile2file(inputurl: str, outputurl: str, session_id: UUID = None):
    session_id, session_data = appvars.get_session_data(session_id)
    headers = {"session_id": session_data.session_id}
    if not session_data.model_loaded:
        reply = JSONResponse({"error": "You need have an active model before you can save."}, headers=headers)
    else:
        try:
            predictor = session_data.model
            _ = predictor.predict_to_file(inputurl,outputurl)
            reply = JSONResponse({"message": F"Predictions written to {outputurl}."}, headers=headers)
        except Exception as e:
            reply = JSONResponse({"error": F"There was an error returning your results: {e}"}, headers=headers)
    return reply

@api.post("/createandtrainmodel/",
          name="Create and Train a New Model Version",
          description="Specify parameters to create a new version of the model and train it with a specified training data file.")
async def createandtrainmodel(name: str, description: str, n_estimators: int,
                              learning_rate: float, max_depth: int,
                              trainingdataurl: str,
                              session_id: UUID = None):
    session_id, session_data = appvars.get_session_data(session_id)
    headers = {"session_id": session_data.session_id}
    try:
        if name == "":
            raise Exception("Name cannot be empty.")
        if description == "":
            raise Exception("Description cannot be empty.")
        predictor = MalignantNetTrafficPredictor(n_estimators=n_estimators, learning_rate=learning_rate, max_depth=max_depth)
        predictor.model_name = name
        description = description + "(estimators: " + str(n_estimators) + ", learning_rate: " + str(learning_rate) + ", max_depth: " + str(max_depth) + ")"
        predictor.model_description = description
        predictor.train(trainingdataurl)
        session_data.model = predictor
        session_data.model_loaded = True
        appvars.update_session_data(session_id, session_data)
        predictor.save_model(name, description, make_filename(name))
        reply = JSONResponse({"message": "New model created, trained, and saved."}, headers=headers)
    except Exception as e:
        reply = JSONResponse({"error": F"There was an error returning your results: {e}"}, headers=headers)
    return reply

def maketempfile():
    cleantempfiles()
    tempdir = "/mntp-data/tmp/"
    if not (os.path.exists(tempdir)):
        os.makedirs(tempdir)
    if not (os.path.isdir(tempdir)):
        raise Exception(f"Path {tempdir} is not a directory.")
    tempfile = __tempfile.NamedTemporaryFile(mode="w+b", dir=tempdir, suffix=".csv", delete=True, delete_on_close=False)
    tmpfilename = str(tempfile.name)
    tempfile.close()
    return tmpfilename

def cleantempfiles():
    tempdir = "/mntp-data/tmp/"
    if os.path.exists(tempdir):
        for entry in os.scandir(tempdir):
            if entry.is_file():
                file_age = int((time.time() - os.stat(entry.path).st_mtime) / 60)
                # os.path.getmtime(entry.path)
                if file_age > 10:
                    os.remove(entry.path)


def make_filename(s):
    """
    Transforms a string into a valid filename by replacing invalid characters with underscores and removing leading/trailing spaces.

    Args:
        s: The input string.

    Returns:
        A valid filename string.
    """
    s = str(s).strip()
    s = re.sub(r'[\\/*?:"<>|]', "_", s)
    return s

if __name__ == "__main__":

    cleantempfiles()
    uvicorn.run(api, host="0.0.0.0", port=80)

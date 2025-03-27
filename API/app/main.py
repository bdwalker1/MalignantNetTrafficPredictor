import os, time
import re
import tempfile as __tempfile
from io import StringIO
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
import uvicorn
import pandas as pd
# from src.SimpleTimer import SimpleTimer
from src.MalignantNetTrafficPredictor import MalignantNetTrafficPredictor

api = FastAPI()

net_predictor = MalignantNetTrafficPredictor()
model_loaded = False

@api.get("/", name="API Demo Page", response_class=HTMLResponse)
async def root():
    return HTMLResponse("Welcome to Malignant Net Traffic Predictor")

@api.post("/listmodels/", name="List Available Models",
          description="List all the models currently available in the container.")
async def list_models():
    dictModels = net_predictor.list_available_models()
        # strList += F"{entry["name"]} - {entry["desc"]} ({entry.name})\n")
    return json.dumps(dictModels, indent=2)

@api.post("/loadedmodel/", name="Show the Currently Loaded Model",
          description="Gets name and description of the currently loaded model.")
async def loaded_model():
    if model_loaded:
        return json.dumps({"name": net_predictor.model_name, "desc": net_predictor.model_description}, indent=2)
    else:
        return json.dumps({"name": "(no model loaded)", "desc": "(no model loaded)"}, indent=2)

@api.post("/getlatestmodel/", name="Get Latest Model", description="Get the latest model from the official GitHub repository.")
async def getlatestmodel():
    global model_loaded
    try:
        net_predictor.retrieve_latest_model()
        model_loaded = True
        print(F"Model name: {net_predictor.model_name}")
        print(F"Description: {net_predictor.model_description}")
        return {"message": F"Retrieved model - Name: {net_predictor.model_name}; Description: {net_predictor.model_description}"}
    except Exception as e:
        return {"error": F"Failed to retrieve latest model. Ensure api container has access to "
                         F"https://github.com/bdwalker1/MalignantNetTrafficPredictor/raw/refs/heads/main/models/"
                         F". Details: {str(e)}"}

@api.post("/getmodelversion/", name="Get Specific Model Version", description="Get a specific model version from the official GitHub repository.")
async def get_modelversion(name: str):
    global model_loaded
    try:
        net_predictor.retrieve_named_model(name)
        model_loaded = True
        print(F"Model name: {net_predictor.model_name}")
        print(F"Description: {net_predictor.model_description}")
        return {"message": F"Retrieved model - Name: {net_predictor.model_name}; Description: {net_predictor.model_description}"}
    except Exception as e:
        return {"error": F"Failed to retrieve model. Ensure model named '{name}' exists at "
                         F"https://github.com/bdwalker1/MalignantNetTrafficPredictor/raw/refs/heads/main/models/ "
                         F"and that your api container has access to that site. Details: {str(e)}"}

@api.post("/savemodel/", name="Save Current Model", description="Save the current model to the user models folder.")
async def save_model(name: str, desc: str, filename: str):
    global model_loaded
    if not(model_loaded):
        return {"error": "You need have an active model before you can save."}
    try:
        net_predictor.save_model(name, desc, filename)
        return {"message": F"Saved model - Name: {name}; Description: {desc}"}
    except Exception as e:
        return {"error": F"Failed to save model. {e}"}

@api.post("/deletemodel/", name="Delete a User-saved Model", description="Delete a user-saved model based on filename.")
async def delete_model(filename: str):
    try:
        net_predictor.delete_model(filename)
        return {"message": F"Deleted user-saved model - Filename: {filename}"}
    except Exception as e:
        return {"error": F"Failed to delete model file. {e}"}

@api.post("/loadofficialmodel/", name="Load Official Model", description="Load a model that has been downloaded from official repository.")
async def loadofficialmodel(filename: str):
    global model_loaded
    try:
        net_predictor.load_official_model(filename)
        model_loaded = True
        print(F"New active model loaded {net_predictor.model_name}")
        return {"message": F"Loaded model - Name: {net_predictor.model_name}; Description: {net_predictor.model_description}"}
    except Exception as e:
        return {"error": F"Failed to load model. {e}"}

@api.post("/loadusermodel/", name="Load a User-Saved Model", description="Load a specific user-saved model.")
async def loadusermodel(filename: str):
    global model_loaded
    try:
        net_predictor.load_user_model(filename)
        model_loaded = True
        print(F"New active model loaded {net_predictor.model_name}")
        return {"message": F"Loaded model - Name: {net_predictor.model_name}; Description: {net_predictor.model_description}"}
    except Exception as e:
        print(F"Failed to load model. {e}")
        return {"error": F"Failed to load model. {e}"}

@api.post("/predictfromjson/",
          name="Predict from JSON Text",
          description="Make predictions from a JSON text string.",
          response_class=JSONResponse)
async def predictfromjson(json_str: str):
    global model_loaded
    if not(model_loaded):
        return {"error": "You need to load a model before you can predict."}
    empty_df = pd.DataFrame([], columns=net_predictor.INPUT_FILE_COLS)
    try:
        input_df = pd.read_json(StringIO(json_str))
        columns_match = True
        # for match in (list(input_df.columns)==list(empty_df.columns)):
        #     columns_match = columns_match & match
        for n, col in enumerate(input_df.columns):
            if col != empty_df.columns[n]:
                columns_match = False
                break
        if columns_match:
            for col in input_df.columns:
                input_df[col] = input_df[col].astype(net_predictor.INPUT_FILE_COLS[col])
            print(input_df.dtypes)
            output_df = net_predictor.predict(input_df)
            print("Returning:" + str(output_df.to_json()))
            return output_df.to_json()
        else:
            return { "Error": "Columns do not match expected input schema."}
    except Exception as e:
        return {"error": F"Exception occurred: {e}"}

@api.post("/predictfromfile/")
async def predictfromfile(fileurl: str):
    global model_loaded
    if not(model_loaded):
        return {"error": "You need to load a model before you can predict."}
    output_df = net_predictor.predictfromfile(fileurl)
    try:
        outputpath = maketempfile()
        output_df.to_csv(path_or_buf=outputpath, sep="|", lineterminator="\n", index=False)
        response = FileResponse(path=outputpath, filename="predictions.csv", media_type="application/csv")
        return response
    except Exception as e:
        return {"error": F"There was an error returning your results: {e}"}

@api.post("/predictfile2file/")
async def predictfile2file(inputurl: str, outputurl: str):
    global model_loaded
    if not(model_loaded):
        return {"error": "You need to load a model before you can predict."}
    _ = net_predictor.predict_to_file(inputurl,outputurl)
    return {"message": F"Predictions written to {outputurl}."}

@api.post("/createandtrainmodel/")
async def createandtrainmodel(name: str, description: str, n_estimators: int, learning_rate: float, max_depth: int, trainingdataurl: str):
    global model_loaded, net_predictor
    net_predictor = MalignantNetTrafficPredictor(n_estimators=n_estimators, learning_rate=learning_rate, max_depth=max_depth)
    net_predictor.model_name = name
    description = description + "(estimators: " + str(n_estimators) + ", learning_rate: " + str(learning_rate) + ", max_depth: " + str(max_depth) + ")"
    net_predictor.model_description = description
    net_predictor.train(trainingdataurl)
    model_loaded = True
    net_predictor.save_model(name, description, make_filename(name))
    return {"message": "New model created, trained, and saved."}

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

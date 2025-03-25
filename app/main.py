import os, time
import tempfile as __tempfile
from io import StringIO
# import numpy as np
from fastapi import FastAPI
# from fastapi.responses import StreamingResponse
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
import pandas as pd
# from src.SimpleTimer import SimpleTimer
from src.MalignantNetTrafficPredictor import MalignantNetTrafficPredictor
import src.MNTP_Website as web

api = FastAPI()

@api.get("/", response_class=HTMLResponse)
async def root():
    return web.landing_page()

@api.post("/getlatestmodel/")
async def getlatestmodel():
    net_predictor = MalignantNetTrafficPredictor(n_estimators=10, learning_rate=1.0, max_depth=4)
    try:
        net_predictor.retrieve_latest_model()
        print(F"Model name: {net_predictor.model_name}")
        print(F"Description: {net_predictor.model_description}")
        net_predictor.save_model("user_model-v0.1",F"Copy of {net_predictor.model_name}", "user_model-v0.1")
        return {"message": F"Retrieved model - Name: {net_predictor.model_name}; Description: {net_predictor.model_description}"}
    except Exception as e:
        return {"error": F"Failed to retrieve latest model. Ensure api container has access to "
                         F"https://github.com/bdwalker1/MalignantNetTrafficPredictor/raw/refs/heads/main/models/"
                         F". Details: {str(e)}"}

@api.post("/getmodelversion/")
async def get_modelversion(name: str):
    net_predictor = MalignantNetTrafficPredictor(n_estimators=10, learning_rate=1.0, max_depth=4)
    try:
        net_predictor.retrieve_named_model(name)
        print(F"Model name: {net_predictor.model_name}")
        print(F"Description: {net_predictor.model_description}")
        return {"message": F"Retrieved model - Name: {net_predictor.model_name}; Description: {net_predictor.model_description}"}
    except Exception as e:
        return {"error": F"Failed to retrieve model. Ensure model named '{name}' exists at "
                         F"https://github.com/bdwalker1/MalignantNetTrafficPredictor/raw/refs/heads/main/models/ "
                         F"and that your api container has access to that site. Details: {str(e)}"}

@api.post("/predictfromjson/")
async def predictfromjson(json_str: str):
    net_predictor = MalignantNetTrafficPredictor()
    print("Loading model from file...")
    net_predictor.load_official_model("MalignantNetTrafficPredictor-latest")
    print(F"Model name: {net_predictor.model_name}")
    print(F"Description: {net_predictor.model_description}")
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
            return output_df.to_json()
        else:
            return { "Error": "Columns do not match expected input schema."}
    except Exception as e:
        return {"error": F"Exception occurred: {e}"}

@api.post("/predictfromfile/")
async def predictfromfile(fileurl: str):
    net_predictor = MalignantNetTrafficPredictor()
    print("Loading model from file...")
    net_predictor.load_official_model("MalignantNetTrafficPredictor-latest")
    print(F"Model name: {net_predictor.model_name}")
    print(F"Description: {net_predictor.model_description}")

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
    net_predictor = MalignantNetTrafficPredictor()
    print("Loading model from file...")
    net_predictor.load_official_model("MalignantNetTrafficPredictor-v0.1")
    print(F"Model name: {net_predictor.model_name}")
    print(F"Description: {net_predictor.model_description}")
    _ = net_predictor.predict_to_file(inputurl,outputurl)
    return {"mesage": F"Predictions written to {outputurl}."}

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

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)

# if __name__ == '__main__':
#     datadir = "G:/My Drive/UCSD_MLE_Bootcamp_Capstone/data/MalwareDetectionInNetworkTrafficData/"
#     if not (os.path.exists(datadir)):
#         datadir = "/Users/bdwalker1/Library/CloudStorage/GoogleDrive-maritz.bruce@gmail.com" + \
#                   "/My Drive/UCSD_MLE_Bootcamp_Capstone/data/MalwareDetectionInNetworkTrafficData/"
#         if not (os.path.exists(datadir)):
#             print("Data path does not exist!")
#
#     print("Instantiating predictor...")
#     net_predictor = MalignantNetTrafficPredictor(n_estimators=10, learning_rate=1.0, max_depth=4)
#     print(net_predictor.get_model())
#
#     # print("Training predictor...")
#     # net_predictor.train(datadir + "training/NTAMalignantTrafficPredictor_Training.csv")
#     # print(net_predictor.get_model())
#     #
#     # print("Saving trained model...")
#     # net_predictor.save_model("MalignantNetTrafficPredictor v0.1","Initial trained model: GradientBoostingClassifier(n_estimators=10, learning_rate=1.0, max_depth=4)", "MalignantNetTrafficPredictor-v0.1.model")
#     # net_predictor.clear_model()
#
#     print("Loading model from file...")
#     net_predictor.load_saved_model("./models/MalignantNetTrafficPredictor-v0.1.model")
#     print(F"Model name: {net_predictor.model_name}")
#     print(F"Description: {net_predictor.model_description}")
#
#     # Import the full data file for prediction comparison
#     print("\nLoading full target file for result comparison...")
#     targetspath = datadir + "testing/full_targets.csv"
#
#     if not (os.path.exists(targetspath)):
#         print(F"Targets file path '{targetspath}' does not exist!")
#
#     dtypes_dict = {'uid': 'string', 'target': 'int32'}
#     targets_df = pd.DataFrame()
#     chucksize = 1000000
#     recs_loaded = 0
#     with pd.read_csv(targetspath, sep="|", low_memory=False, dtype=dtypes_dict,
#                      chunksize=chucksize) as reader:
#         for df in reader:
#             targets_df = pd.concat([targets_df, df])
#             recs_loaded += df.shape[0]
#             print(f"\r{recs_loaded:>10} records loaded", end='')
#
#     targets_df.set_index('uid', inplace=True)
#     print(f"\r{recs_loaded:>10} total records.         ")
#
#     # Make predictions on test file
#     print("\nLoading/predicting from test file...")
#     testdir = datadir + "testing/"
#     tmr = SimpleTimer()
#     tmr.start()
#     output_df = net_predictor.predict(testdir + "NTAMalignantTrafficPredictor_Testing.csv")
#     output_df.set_index('uid', inplace=True)
#     print(f"Load/Prediction time: {tmr.sts(tmr.laptime())}")
#
#     merge_df = targets_df.join(output_df, how="inner")
#     print(f"Merge time: {tmr.sts(tmr.laptime())}")
#
#     diff_df = merge_df[["target", "prediction"]].loc[(merge_df["target"] != merge_df["prediction"])]
#     print(f"Diff time: {tmr.sts(tmr.laptime())}")
#
#     print(f"\nMis-predictions / Total records: {diff_df.shape[0]} / {output_df.shape[0]}")
#     print(f"Bad prediction rate:{(diff_df.shape[0]/output_df.shape[0]):0.2%}")
#     del output_df, merge_df, diff_df
#     _ = tmr.stop()
#
#     # Test model on full dataset
#     print("\nLoading/predicting from full dataset file...")
#     _ = tmr.reset()
#     _ = tmr.start()
#     output_df = net_predictor.predict(testdir + "NTAMalignantTrafficPredictor_Full.csv")
#     output_df.set_index('uid', inplace=True)
#     print(f"Load/Prediction time: {tmr.sts(tmr.laptime())}")
#
#     merge_df = targets_df.join(output_df, how="inner")
#     print(f"Merge time: {tmr.sts(tmr.laptime())}")
#
#     diff_df = merge_df[["target", "prediction"]].loc[(merge_df["target"] != merge_df["prediction"])]
#     print(f"Diff time: {tmr.sts(tmr.laptime())}")
#
#     print(f"\nMis-predictions / Total records: {diff_df.shape[0]} / {merge_df.shape[0]}")
#     print(f"Bad prediction rate:{(diff_df.shape[0]/merge_df.shape[0]):0.2%}")
#     del output_df, merge_df, diff_df
#     _ = tmr.stop()

import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn
import pandas as pd
from app.src.SimpleTimer import SimpleTimer
from app.src.MalignantNetTrafficPredictor import MalignantNetTrafficPredictor

api = FastAPI()

@api.get("/")
async def root():
    return {"message": "Welcome to Malignant Net Traffic Predictor"}

@api.post("/predictfromfile/")
async def predict(fileurl: str):
    net_predictor = MalignantNetTrafficPredictor(n_estimators=10, learning_rate=1.0, max_depth=4)
    print("Loading model from file...")
    net_predictor.load_saved_model("./models/MalignantNetTrafficPredictor-v0.1.model")
    print(F"Model name: {net_predictor.model_name}")
    print(F"Description: {net_predictor.model_description}")
    output_df = net_predictor.predict(fileurl)
    # output_data = output_df.to_csv(index=False, header=True, sep="|", lineterminator="\n")
    return output_df.to_json()
    # return StreamingResponse(output_data, media_type="text/csv")

@api.post("/predictfile2file/")
async def predict(inputurl: str, outputurl: str):
    net_predictor = MalignantNetTrafficPredictor(n_estimators=10, learning_rate=1.0, max_depth=4)
    print("Loading model from file...")
    net_predictor.load_saved_model("./models/MalignantNetTrafficPredictor-v0.1.model")
    print(F"Model name: {net_predictor.model_name}")
    print(F"Description: {net_predictor.model_description}")
    output_df = net_predictor.predict_to_file(inputurl,outputurl)
    # output_data = output_df.to_csv(index=False, header=True, sep="|", lineterminator="\n")
    # return output_df.to_json()
    return {"mesage": F"Predictions written to {outputurl}."}

if __name__ == "__main__":
    uvicorn.run(api, host="127.0.0.1", port=8000)

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

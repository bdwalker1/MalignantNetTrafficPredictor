import os
import requests
# from pathlib import Path
import joblib
import numpy as np
import datetime as dt
import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import MinMaxScaler
# from sklearn.model_selection import train_test_split
# from sklearn.model_selection import cross_val_score
# from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
# from sklearn.metrics import PrecisionRecallDisplay as PRDisp
from src.SimpleTimer import SimpleTimer

class MalignantNetTrafficPredictor:
    MODELS_GITHUB_URL = "https://github.com/bdwalker1/MalignantNetTrafficPredictor/raw/refs/heads/main/API/models/"
    INPUT_FILE_CHUNKSIZE = 5000000
    TRAINING_FILE_COLS = {
        "id.orig_p": "int32",
        "id.resp_p": "int32",
        "proto": "string",
        "service": "string",
        "conn_state": "string",
        "history": "string",
        "orig_pkts": "int32",
        "orig_ip_bytes": "int32",
        "resp_pkts": "int32",
        "resp_ip_bytes": "int32",
        "day_of_week": "int32",
        "day_of_month": "int32",
        "hour_of_day": "int32",
        "target": "int32",
    }
    INPUT_FILE_COLS = {
        "ts": "float64",
        "uid": "string",
        "id.orig_p": "int32",
        "id.resp_p": "int32",
        "proto": "string",
        "service": "string",
        "conn_state": "string",
        "history": "string",
        "orig_pkts": "int32",
        "orig_ip_bytes": "int32",
        "resp_pkts": "int32",
        "resp_ip_bytes": "int32",
    }
    ONEHOT_COLS = [
        "proto",
        "service",
        "conn_state",
        "history",
    ]
    SCALE_COLS = [
        "orig_ip_bytes",
        "orig_pkts",
        "resp_ip_bytes",
        "resp_pkts",
    ]

    def __init__(self, n_estimators=10, learning_rate=1.0, max_depth=4, random_state=None):
        # Set class parameters
        self.__n_estimators = n_estimators
        self.__learning_rate = learning_rate
        self.__max_depth = max_depth
        self.__random_state = random_state
        self.__training_df = pd.DataFrame(columns=list(self.TRAINING_FILE_COLS.keys()))
        self.__predict_df = pd.DataFrame(columns=list(self.INPUT_FILE_COLS.keys()))
        self.__encoders = dict()

        self.__predictor = GradientBoostingClassifier(n_estimators=self.__n_estimators,
                                                      learning_rate=self.__learning_rate,
                                                      max_depth=self.__max_depth,
                                                      random_state=self.__random_state)
        self.model_name = ""
        self.model_description = ""
        return

    @staticmethod
    def __downlaod_file(url, local_filepath):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(local_filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=4096):
                    f.write(chunk)
            print(F"File {url} downloaded to {local_filepath}")
        except requests.exceptions.RequestException as e:
            raise Exception(F"Failed to retrieve file. Error occurred: {e}")
        return

    def __get_model_from_repo(self, model_name):
        repo_model_url_prefix = self.MODELS_GITHUB_URL
        model_extension = ".model"

        request_url = repo_model_url_prefix + model_name + model_extension
        local_model_path = "./models/" + model_name + model_extension

        try:
            self.__downlaod_file(request_url, local_model_path)
        except Exception as e:
            raise Exception(F"Failed to download model. Error occurred: {e}")
        return

    def __onehot_encode(self, colname, df, train=False):
        if colname not in df.columns:
            raise Exception(f"Column '{colname}' not in dataframe.")
        if train:
            self.__encoders[colname] = OneHotEncoder(sparse_output=False, dtype=np.uint8,
                                                     handle_unknown='ignore').set_output(transform="pandas")
            _ = self.__encoders[colname].fit(df[[colname]])

        coded_df = self.__encoders[colname].transform(df[[colname]])
        df = pd.concat([df, coded_df], axis=1)
        df.drop(colname, axis=1, inplace=True)
        del coded_df

        return df

    def __scale_encode(self, colname, df, train=False):
        if colname not in df.columns:
            raise Exception(f"Column '{colname}' not in dataframe.")
        if train:
            self.__encoders[colname] = MinMaxScaler()
            _ = self.__encoders[colname].fit(df[[colname]])

        df[colname] = self.__encoders[colname].transform(df[[colname]])

        return df

    def __preprocess(self, df, train=False):
        for col in self.ONEHOT_COLS:
            df = self.__onehot_encode(col, df, train=train)

        for col in self.SCALE_COLS:
            df = self.__scale_encode(col, df, train=train)

        return df

    @staticmethod
    def __prepare_input(df):
        prep_df = df.drop("uid", axis=1)
        prep_df["date_time"] = prep_df["ts"].apply(dt.datetime.fromtimestamp)
        prep_df["day_of_week"] = prep_df["date_time"].dt.dayofweek
        prep_df["day_of_week"] = prep_df["day_of_week"].astype(np.uint8)
        prep_df["day_of_month"] = prep_df["date_time"].dt.day
        prep_df["day_of_month"] = prep_df["day_of_month"].astype(np.uint8)
        prep_df["hour_of_day"] = prep_df["date_time"].dt.hour
        prep_df["hour_of_day"] = prep_df["hour_of_day"].astype(np.uint8)

        # Drop the raw timestamp and date/time columns
        prep_df.drop("date_time", axis=1, inplace=True)
        prep_df.drop("ts", axis=1, inplace=True)

        return prep_df

    def __load_trainingfile(self, filepath):
        # if not (os.path.exists(filepath)):
        #     raise FileNotFoundError(f"File not found: {filepath}")
        # if not (os.path.isfile(filepath)):
        #     raise FileNotFoundError(f"Specified path is not a file: {filepath}")

        self.__training_df = pd.read_csv(filepath, sep="|", low_memory=False, dtype=self.TRAINING_FILE_COLS)
        print(f"Training data shape: {self.__training_df.shape}")
        return self.__training_df

    def __load_datafile(self, filepath):
        # if not (os.path.exists(filepath)):
        #     raise FileNotFoundError(f"File not found: {filepath}")
        # if not (os.path.isfile(filepath)):
        #     raise FileNotFoundError(f"Specified path is not a file: {filepath}")

        load_df = pd.read_csv(filepath, sep="|", low_memory=False, dtype=self.INPUT_FILE_COLS)
        print(f"Input data shape: {load_df.shape}")
        return load_df

    @staticmethod
    def __verify_expected_storage_dirs():
        user_model_dir = '/mntp-data/models_user/'
        if not(os.path.exists(user_model_dir)):
            os.makedirs(user_model_dir)
        output_dir = '/mntp-data/output/'
        if not(os.path.exists(output_dir)):
            os.makedirs(output_dir)

    def train(self, filepath):
        self.__load_trainingfile(filepath)
        self.__training_df = self.__preprocess(self.__training_df, train=True)
        y = self.__training_df["target"]
        x = self.__training_df.drop("target", axis=1)
        self.__predictor.fit(x, y)
        return

    def predictfromfile(self, filepath: str):
        # Load file(s) / Verify data format
        input_df = self.__load_datafile(filepath)
        output_df = self.predict(input_df)
        return output_df

    def predict(self, input_df: pd.DataFrame):

        # Pre-process data
        self.__predict_df = self.__prepare_input(input_df)
        self.__predict_df = self.__preprocess(self.__predict_df, train=False)

        y_pred = self.__predictor.predict(self.__predict_df)

        output_df = pd.concat([input_df[["uid"]], pd.DataFrame(y_pred, columns=["prediction"])], axis=1)
        return output_df

    def predict_to_file(self, inputpath: str, outputpath: str):

        # input_filename = os.path.basename(inputpath)
        # file_ext = Path(input_filename).suffix
        output_dir = os.path.dirname(outputpath)
        # output_filename = os.path.basename(outputpath)
        if not(os.path.exists(output_dir)):
            os.makedirs(output_dir)
        first_pass = True
        chunk_tmr = SimpleTimer()
        chunk_tmr.start()
        for input_chunk_df in pd.read_csv(inputpath, sep="|", low_memory=False, dtype=self.INPUT_FILE_COLS,
                                          chunksize=self.INPUT_FILE_CHUNKSIZE):

            print(f"Chunk read time: {chunk_tmr.sts(chunk_tmr.laptime())}")

            this_chunk = input_chunk_df.reset_index(drop=True)

            # Pre-process data
            predict_df = self.__prepare_input(this_chunk)
            predict_df = self.__preprocess(predict_df, train=False)
            print(f"Chunk process time: {chunk_tmr.sts(chunk_tmr.laptime())}")

            y_pred = self.__predictor.predict(predict_df)
            print(f"Chunk predict time: {chunk_tmr.sts(chunk_tmr.laptime())}")

            output_df = pd.concat([this_chunk[["uid"]], pd.DataFrame(y_pred, columns=["prediction"])], axis=1)
            del y_pred

            _ = output_df.to_csv(outputpath, sep="|", mode="a", header=first_pass, index=False)
            del output_df
            print(f"Chunk output time: {chunk_tmr.sts(chunk_tmr.laptime())}")

            chunk_tmr.stop()
            chunk_tmr.start()
            first_pass = False

        return True

    def get_model(self):
        return self.__predictor

    def __load__model_file(self, filepath):
        loaded_model = joblib.load(filepath)
        self.model_name = loaded_model['name']
        self.model_description = loaded_model['desc']
        self.__predictor = loaded_model['model']
        self.__encoders = loaded_model['encoders']
        return

    def load_official_model(self, filename):
        filepath = "./models/" + filename + ".model"
        self.__load__model_file(filepath)
        return

    def load_user_model(self, filename):
        filepath = "/mntp-data/models_user/" + filename + ".model"
        self.__load__model_file(filepath)
        return

    def save_model(self, name, desc, filename):
        if os.path.basename(filename) != filename:
            raise ValueError(f"You must specify only a filename, not a path.")
        user_model_path = "/mntp-data/models_user/"
        if not(os.path.exists(user_model_path)):
            os.makedirs(user_model_path)
        if not(os.path.isdir(user_model_path)):
            raise NotADirectoryError(f"{user_model_path} is not a directory")
        filepath = user_model_path + filename + ".model"
        model_to_save = dict()
        model_to_save['name'] = name
        model_to_save['desc'] = desc
        model_to_save['model'] = self.__predictor
        model_to_save['encoders'] = self.__encoders
        joblib.dump(model_to_save, filepath)
        return

    def delete_model(self, filename):
        if os.path.basename(filename) != filename:
            raise ValueError(f"You must specify only a filename, not a path.")
        if filename.endswith(".model"):
            filename = str(os.path.basename(filename)).removesuffix(".model")
        self.__verify_expected_storage_dirs()
        user_model_path = "/mntp-data/models_user/"
        if not(os.path.exists(user_model_path)):
            os.makedirs(user_model_path)
        if not(os.path.isdir(user_model_path)):
            raise NotADirectoryError(f"{user_model_path} is not a directory")
        filepath = user_model_path + filename + ".model"
        if not(os.path.exists(filepath)):
            raise FileNotFoundError(f"{filepath} does not exist")
        os.remove(filepath)
        return

    def clear_model(self):
        self.__predictor = None
        self.__encoders = None
        return

    def retrieve_latest_model(self):
        self.retrieve_named_model("MalignantNetTrafficPredictor-latest")
        return

    def retrieve_named_model(self, name: str):
        self.__get_model_from_repo(name)
        self.load_official_model(name)
        return

    def list_available_models(self):
        self.__verify_expected_storage_dirs()
        print(F"Listing available models...")
        model_list = {}
        tmp_model = MalignantNetTrafficPredictor()
        for entry in os.scandir("./models"):
            if entry.name.endswith(".model"):
                filename = str(os.path.basename(entry.name)).removesuffix(".model")
                tmp_model.load_official_model(filename)
                model_list[tmp_model.model_name] = { "type": "official", "name": tmp_model.model_name,
                                                     "desc": tmp_model.model_description, "filename": filename}
        for entry in os.scandir("/mntp-data/models_user"):
            if str(entry.name).endswith(".model"):
                filename = str(os.path.basename(entry.name)).removesuffix(".model")
                tmp_model.load_user_model(filename)
                model_list[tmp_model.model_name] = { "type": "user", "name": tmp_model.model_name,
                                                     "desc": tmp_model.model_description, "filename": filename}
        return model_list

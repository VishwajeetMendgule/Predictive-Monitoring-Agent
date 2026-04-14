import joblib 
from Process_logs import processed_logs
import pandas as pd
import matplotlib.pyplot as plt
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' # To Surppress all logs/warnings

from tensorflow import keras 

def prediction_model():

    logs = processed_logs()


    scaler = joblib.load("data_scaler.pkl")
    pass


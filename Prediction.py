import joblib 
from Process_logs import processed_logs
import numpy as np
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' # To Surppress all logs/warnings

from tensorflow import keras 

def create_lstm_sequences(data_array, time_steps=5):
    """
    Converts a 2D array into a 3D array [samples, time_steps, features] for LSTM training.
    """
    X, y = [], []
    
    # Here basically we are dividing dataset such that 5 rows in x and 6th row in Y as target 
    for i in range(len(data_array) - time_steps):
        # The past 5 minutes
        window = data_array[i : (i + time_steps)]
        X.append(window)
        
        # The 6th minute (the target we want to predict)
        target = data_array[i + time_steps]
        y.append(target)
        
        # Finally creating it to a np array
    return np.array(X), np.array(y)

def train_predictionmodel():

    logs = processed_logs()
    
    scaler = joblib.load("data_scaler.pkl")

    logs_scaled = scaler.transform(logs.values)  # data to be used for traning
    # print(logs_scaled)

x,y = create_lstm_sequences(processed_logs().values)
print("This is x")
print(x)
print("This is Y")
print(y)
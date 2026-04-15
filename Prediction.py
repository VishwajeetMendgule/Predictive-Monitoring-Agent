import joblib 
import numpy as np
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' # To Surppress all logs/warnings

from tensorflow import keras 
from tensorflow.keras.models import load_model

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

def train_predictionmodel(data):

    scaler = joblib.load("data_scaler.pkl")
    
    scaleddata = scaler.transform(data.values) # data to be used for traning
    x_train,y_train = create_lstm_sequences(scaleddata)


    model = keras.models.Sequential()

    # First Layer
    model.add(keras.layers.LSTM(64, return_sequences = True, input_shape = (x_train.shape[1], x_train.shape[2])))

    # Secound Layer
    model.add(keras.layers.LSTM(128, return_sequences = False))

    # Third Layer
    model.add(keras.layers.Dense(128,activation="relu"))
    
    # Fourth Layer to drop some data
    model.add(keras.layers.Dropout(0.2))

    #final layer 
    model.add(keras.layers.Dense(x_train.shape[2]))

    model.summary()
    model.compile(optimizer='adam', loss="mae",metrics=[keras.metrics.RootMeanSquaredError()])

    traning = model.fit(x_train, y_train, epochs= 50, batch_size = 32)

    model.save('lstm_model.keras')

    return model

def lstm_model(data):
    scaler = joblib.load("data_scaler.pkl")

    try:
        model = load_model('lstm_model.keras')
    except Exception as e:
        print(f"Model not found. ERROR \n {e}")
        return None
    
    data_scaled = scaler.transform(data.values)
    x_test,_ = create_lstm_sequences(data_scaled)
     
    predictions = model.predict(x_test)
    predictions = scaler.inverse_transform(predictions)

    return predictions

 

# For Traning model 
# from ReadLogs import readtrainlogs
# from Process_logs import processed_logs
# logs,cpu,memory,network = readtrainlogs()

# train = processed_logs(logs,cpu,memory,network)

# train_predictionmodel(train)
import joblib 
import numpy as np
import os
import logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' # To Surppress all logs/warnings

from tensorflow import keras 
from tensorflow.keras.models import load_model
import tensorflow as tf

# 3. Silence the Python-level warnings (This fixes the GPU warning)
tf.get_logger().setLevel('ERROR')
logging.getLogger('tensorflow').setLevel(logging.ERROR)

def create_lstm_sequences(data, time_steps=5, lookahead_steps=3):
    """
    time_steps: How many past minutes to look at (e.g., 5)
    lookahead_steps: How many minutes into the future to predict 
                     (1 = 6th min, 2 = 7th min, 3 = 8th min)
    """
    x, y = [], []
    
    # We must stop early enough so we don't reach out of bounds looking for 'y'
    for i in range(len(data) - time_steps - (lookahead_steps - 1)):
        # X gets the 5 consecutive minutes
        x.append(data[i : i + time_steps])
        
        # Y gets the single minute that is 'lookahead_steps' ahead
        target_index = i + time_steps + (lookahead_steps - 1)
        y.append(data[target_index])
        
    return np.array(x), np.array(y)

def train_predictionmodel(data):

    scaler = joblib.load("lstm_scaler.pkl")
    
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
    scaler = joblib.load("lstm_scaler.pkl")

    try:
        model = load_model('lstm_model.keras')
    except Exception as e:
        print(f"Model not found. ERROR \n {e}")
        return None
    data_scaled = scaler.transform(data.values)
    if data.__len__() != 5:
    
      x_test,_ = create_lstm_sequences(data_scaled)
    else :
        x_test = np.array([data_scaled])
    predictions = model.predict(x_test)
    predictions = scaler.inverse_transform(predictions)

    return predictions

 

# For Traning model 
# from ReadLogs import readtrainlogs
# from Process_logs import processed_logs
# logs,cpu,memory,network = readtrainlogs()

# train = processed_logs(logs,cpu,memory,network)

# train_predictionmodel(train)

# from sklearn.preprocessing import MinMaxScaler

# lstm_scaler = MinMaxScaler(feature_range=(0, 1))
# lstm_scaler.fit_transform(train.values)
    
#     # ... train model ...
# joblib.dump(lstm_scaler, 'lstm_scaler.pkl')
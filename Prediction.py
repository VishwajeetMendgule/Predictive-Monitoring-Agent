import joblib 
import pandas as pd
import matplotlib.pyplot as plt
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' # To Surppress all logs/warnings

from tensorflow import keras 

def prediction_model():


    scaler = joblib.load("data_scaler.pkl")
    pass

# model = keras.models.Sequential()
cpu = pd.read_csv('cpu_test.csv').rename(columns={'value': 'cpu'})[['timestamp','cpu']]
memory = pd.read_csv('mem_test.csv').rename(columns={'value': 'memory'})[['timestamp','memory']]
network = pd.read_csv('net_test.csv').rename(columns={'value': 'network'})[['timestamp','network']]

cpu['time'] = pd.to_datetime(cpu['timestamp']).dt.strftime('%M:%S')
memory['time'] = pd.to_datetime(memory['timestamp']).dt.strftime('%M:%S')
network['time'] = pd.to_datetime(network['timestamp']).dt.strftime('%M:%S')

plt.plot(cpu['time'].values,cpu['cpu'].values)
plt.plot(memory['time'].values,memory['memory'].values)
plt.plot(network['time'].values,network['network'].values)
plt.xlabel("Time") 
plt.ylabel("Values") 
plt.legend()
plt.show()
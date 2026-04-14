from ReadLogs import readtestlogs,readtrainlogs
from Prediction import lstm_model
from Process_logs import processed_logs
import matplotlib.pyplot as plt

logs,cpu,memory,network = readtestlogs()

test = processed_logs(logs,cpu,memory,network)

logs,cpu,memory,network = readtrainlogs()

train = processed_logs(logs,cpu,memory,network)

predictions = lstm_model()

test = test.copy()

test['Prediction'] = predictions

plt.figure(figsize=(12,8))
plt.plot()


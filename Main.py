from ReadLogs import readtestlogs,readtrainlogs
from Prediction import lstm_model
from Process_logs import processed_logs
from Anomaly_model import Anomaly_model 
from Response import generate_answer
import json
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

logs,cpu,memory,network = readtestlogs()

test = processed_logs(logs,cpu,memory,network)
# print(test.__len__())
am = Anomaly_model()
Anomaly = am.an_model(test)

# print(Anomaly)
predictions = lstm_model(test.tail(5)) # passing only last 5 mins 

predictions = {"Predicted_CPU": f"{predictions[0,0]:.2f}%",
               "Predicted_Memory": f"{predictions[0,1]:.2f}%",
               "Predicted_Network": f"{predictions[0,2]:.2f}",
               "Predicted_Errors": int(predictions[0, 4])}

future_data = json.dumps(predictions,indent=2)
current_dict = test[['cpu','memory','network','ERROR','WARN']].iloc[-1].to_dict()
current = json.dumps(current_dict,indent=2)
applogs = json.dumps(logs[['level','component','message']].iloc[-1].to_dict(),indent=2)

print(generate_answer(future_data,current,applogs))

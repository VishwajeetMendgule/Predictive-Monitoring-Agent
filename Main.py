from ReadLogs import readtestlogs,readtrainlogs
from Prediction import lstm_model
from Process_logs import processed_logs
from Anomaly_model import Anomaly_model 
from Response import generate_answer,Model_prompt
import json,time,requests,sqlite3,os
import pandas as pd

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

last_time = None

while True:

    try:
        logs,cpu,memory,network = readtestlogs()

        if cpu.empty or memory.empty:
                time.sleep(3)
                continue

        test = processed_logs(logs,cpu,memory,network)
        conn = sqlite3.connect('logs.db')

        log_time = test['timestamp'].iloc[-1].strftime("%H:%M:%S")

        if log_time == last_time:
            time.sleep(1) # Wait 1 second and check the files again
            continue
            
        # 3. Update the tracker to the new time
        last_time = log_time

        old_record = pd.DataFrame([{
            "timestamp": test['timestamp'].iloc[-1].strftime("%Y-%m-%d %H:%M:%S"), 
            "cpu": float(test.iloc[-1]['cpu']),
            "memory": float(test.iloc[-1]['memory']),
            "network": float(test.iloc[-1]['network'])
        }])

        old_record.to_sql('server_metrics', conn, if_exists='append', index=False)

        test = test[['cpu','memory','network','DEBUG','ERROR','INFO','WARN']].copy()
        am = Anomaly_model()
        Anomaly = am.an_model(test.tail(2))

        current_row = test.iloc[-1]

        payload = {
            "timestamp": log_time,  
            "cpu": round(float(current_row['cpu']), 1),
            "memory": round(float(current_row['memory']), 1),
            "network": round(float(current_row['network']), 1),
            "is_anomaly": False
        }

        # print(Anomaly)
        if not Anomaly.empty:
            payload["is_anomaly"] = True
            predictions = lstm_model(test.tail(5)) # passing only last 5 mins 

            # predictions = {"Predicted_CPU": f"{predictions[0,0]:.2f}%",
            #            "Predicted_Memory": f"{predictions[0,1]:.2f}%",
            #            "Predicted_Network": f"{predictions[0,2]:.2f}",
            #            "Predicted_Errors": int(predictions[0, 4])}

            payload["predicted_cpu"] = round(float(predictions[0, 0]), 1)
            payload["predicted_memory"] = round(float(predictions[0, 1]), 1)
            payload["predicted_network"] = round(float(predictions[0, 2]), 1)

            # LLM Integration 

            # future_data = json.dumps(predictions,indent=2)
            current_dict = test[['cpu','memory','network','ERROR','WARN']].iloc[-1].to_dict()
            current = json.dumps(current_dict,indent=2)
            applogs = json.dumps(logs[['level','component','message']].iloc[-1].to_dict(),indent=2)
            # prompt = Model_prompt(future_data,current,applogs)
            # Response = json.loads(generate_answer(prompt))
            # print(f"Severity: {Response["severity"]}")
            # print(f"Root cause: {Response["failure_type"]}")
            # print(f"Impact In: {Response["impactmins"]}mins")
            # print(f"Recommended Action: {Response["RecommendedAction"]}")
            # This will be in above format as for testing it hardcoded
            payload["llm_response"] = {
                    "severity": "CRITICAL",
                    "failure_type": "JVM OutOfMemory / Thread Starvation",
                    "RootCause": "Application is retaining objects in memory leading to GC overhead and network timeout.",
                    "impactmins": 5,
                    "RecommendedAction": "Trigger auto-scaling group and restart failing JVM instances."
                }
            print(f"{predictions}")

        else:
            print("✅ System is stable.")
            # This block will tigure only if anomaly is not deteceted 


        response = requests.post('http://localhost:3000/api/telemetry', json=payload)

        time.sleep(2) # Sleep before checking for new logs


    except Exception as e:
        print(f"⚠️ Error: {e}")
        time.sleep(5)

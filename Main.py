from ReadLogs import readtestlogs,readtrainlogs
from Prediction import lstm_model
from Process_logs import processed_logs
from Anomaly_model import Anomaly_model 
from Response import generate_answer,Model_prompt
from Alert import send_alert_email
from DB_query import check_maintenance_mode
import json,time,requests,sqlite3,threading
import pandas as pd


def parse_llm_response(response_text):
    if not response_text:
        return None
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        start = response_text.find('{')
        end = response_text.rfind('}')
        if start >= 0 and end > start:
            try:
                return json.loads(response_text[start:end+1])
            except json.JSONDecodeError:
                pass
    return None

processed_time = pd.to_datetime('2000-01-01', utc=True)
last_alert_time = None
cached_llm_response = None
alert_cooldown_minutes = 5

while True:

    try:
        logs,cpu,memory,network = readtestlogs()

        if cpu.empty or memory.empty:
                time.sleep(3)
                continue

        test = processed_logs(logs,cpu,memory,network)

        test_temp = test[test['timestamp'] > processed_time]

        if test_temp.empty:
            # If everything was old, go back to sleep
            time.sleep(1)
            continue

        processed_time = test['timestamp'].iloc[-1]
        
        conn = sqlite3.connect('D:/Preditictive Agent/logs.db')

        log_time = test['timestamp'].iloc[-1].strftime("%H:%M:%S")

        old_record = pd.DataFrame([{
            "timestamp": test['timestamp'].iloc[-1].strftime("%Y-%m-%d %H:%M:%S"), 
            "cpu": float(test.iloc[-1]['cpu']),
            "memory": float(test.iloc[-1]['memory']),
            "network": float(test.iloc[-1]['network'])
        }])

        old_record.to_sql('server_metrics', conn, if_exists='append', index=False)

        is_maintenance, maint_reason = check_maintenance_mode(processed_time,conn)

        conn.close()

        test = test[['cpu','memory','network','DEBUG','ERROR','INFO','WARN']].copy()
        am = Anomaly_model()
        Anomaly = am.an_model(test.tail(2))

        current_row = test.iloc[-1]

        payload = {
            "timestamp": log_time,  
            "cpu": round(float(current_row['cpu']), 1),
            "memory": round(float(current_row['memory']), 1),
            "network": round(float(current_row['network']), 1),
            "is_anomaly": False,
            "maintenance_active": is_maintenance, # Tell the UI!
            "maintenance_reason": maint_reason
        }
        if is_maintenance:
            print(f"🔕 MAINTENANCE MODE ACTIVE: Bypassing alerts. Reason: {maint_reason}")

        else:    

            # print(Anomaly)
            if not Anomaly.empty:
                payload["is_anomaly"] = True
                predictions = lstm_model(test.tail(5)) # passing only last 5 mins 

                payload["predicted_cpu"] = round(float(predictions[0, 0]), 1)
                payload["predicted_memory"] = round(float(predictions[0, 1]), 1)
                payload["predicted_network"] = round(float(predictions[0, 2]), 1)

                # Alert Debounce / Cooldown Mechanism
                current_timestamp = processed_time
                should_alert = False
                
                if last_alert_time is None:
                    should_alert = True
                else:
                    # Use pandas timestamp subtraction for safe datetime operations
                    time_since_last_alert = current_timestamp - last_alert_time
                    if time_since_last_alert > pd.Timedelta(minutes=alert_cooldown_minutes):
                        should_alert = True
                
                if should_alert:
                    # Execute LLM call and email trigger
                    print(f"🚨 Anomaly detected! Running LLM analysis...")
                    
                    future_data = json.dumps(predictions.tolist(), indent=2)
                    current_dict = test[['cpu','memory','network','ERROR','WARN']].iloc[-1].to_dict()
                    current = json.dumps(current_dict, indent=2)
                    applogs = json.dumps(logs[['level','component','message']].iloc[-1].to_dict(), indent=2)
                    prompt = Model_prompt(future_data, current, applogs)
                    llm_response = generate_answer(prompt)
                    
                    if llm_response:
                        parsed_response = parse_llm_response(llm_response)
                        if parsed_response:
                            cached_llm_response = parsed_response
                        else:
                            cached_llm_response = {
                                "severity": "UNKNOWN",
                                "failure_type": "LLM Response Parse Error",
                                "RootCause": "LLM returned invalid JSON response.",
                                "impactmins": 0,
                                "RecommendedAction": "Check LLM API response format."
                            }
                    else:
                        cached_llm_response = {
                            "severity": "UNKNOWN",
                            "failure_type": "LLM Error",
                            "RootCause": "Failed to get response from LLM.",
                            "impactmins": 0,
                            "RecommendedAction": "Check API key and network."
                        }
                    
                    payload["llm_response"] = cached_llm_response
                    last_alert_time = current_timestamp
                    
                    # Trigger email alert
                    admin_email = "vishwajeetmendgule08@outlook.com" 
                    email_thread = threading.Thread(
                        target=send_alert_email, 
                        args=(payload, admin_email)
                    )
                    email_thread.start()
                    print(f"📧 Alert email queued.")
                else:
                    # Within cooldown window: use cached response
                    time_since_last_alert = current_timestamp - last_alert_time
                    print(f"⏱️  Anomaly persists (cooldown active: {time_since_last_alert.total_seconds():.0f}s/{alert_cooldown_minutes*60}s). Using cached LLM response.")
                    if cached_llm_response:
                        payload["llm_response"] = cached_llm_response
                    else:
                        payload["llm_response"] = {
                            "severity": "WARNING",
                            "failure_type": "Ongoing Anomaly",
                            "RootCause": "Anomaly still active from previous analysis.",
                            "impactmins": 0,
                            "RecommendedAction": "Monitor system closely."
                        }
                
                print(f"Predictions: {predictions}")

            else:
                print("✅ System is stable.")
                # This block will tigure only if anomaly is not deteceted 
                last_alert_time = None
                cached_llm_response = None


        response = requests.post('http://localhost:3000/api/telemetry', json=payload)

        time.sleep(2) # Sleep before checking for new logs


    except Exception as e:
        print(f"⚠️ Error: {e}")
        time.sleep(3)

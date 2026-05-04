import pandas as pd
import numpy as np
import json,time,math,random
import os
from datetime import datetime, timedelta

# Helper function to append to CSV without duplicating headers
def append_csv(filename, row_data, columns):
    df = pd.DataFrame([row_data], columns=columns)
    # If file doesn't exist, create it and write headers. Otherwise, append.
    if not os.path.isfile(filename):
        df.to_csv(filename, index=False)
    else:
        df.to_csv(filename, mode='a', header=False, index=False)

def live_log_generator():
    hostname = "prod-web-srv-01"
    current_time = datetime.now()
    
    print("🚀 Starting Live Log Generator...")
    print("Writing 1 simulated minute of data every 3 seconds. Press Ctrl+C to stop.")

    # State Machine Variables
    state = "NORMAL"
    minutes_in_current_state = 0

    while True:
        try:
            # 1. Advance simulation time by 1 minute
            current_time += timedelta(minutes=1)
            ts_str = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            logs = []

            # -------------------------------------------------
            # STATE TRANSITION LOGIC
            # -------------------------------------------------
            minutes_in_current_state += 1

            if state == "NORMAL":
                # After 4 normal minutes, introduce a 25% chance to start failing
                if minutes_in_current_state >= 4 and random.random() < 0.25:
                    state = "FAILING"
                    minutes_in_current_state = 0
                    print(f"\n[{ts_str}] ⚠️ SIMULATION TRIGGER: Anomaly Started!")
            
            elif state == "FAILING":
                # Recover automatically after 5 minutes of failure
                if minutes_in_current_state >= 5:
                    state = "NORMAL"
                    minutes_in_current_state = 0
                    print(f"\n[{ts_str}] ✅ SIMULATION TRIGGER: System Recovered!")

            # -------------------------------------------------
            # DATA GENERATION BASED ON STATE
            # -------------------------------------------------
            # Create a subtle wave based on the time of day
            total_minutes_today = current_time.hour * 60 + current_time.minute
            time_of_day_multiplier = (math.sin(total_minutes_today * (2 * math.pi / 1440)) + 1) / 2 

            if state == "NORMAL":
                # Stable Metrics
                cpu = 40 + (10 * time_of_day_multiplier) + np.random.normal(0, 2)
                mem = 50 + (10 * time_of_day_multiplier) + np.random.normal(0, 1)
                net = 100 + (300 * time_of_day_multiplier) + np.random.normal(0, 10)
                
                # Normal Logs
                if random.random() < 0.6:
                    logs.append({"timestamp": ts_str, "level": "INFO", "component": "system", "message": "Health check OK."})
            
            elif state == "FAILING":
                # Metrics spike based on how long it's been failing
                anomaly_progress = minutes_in_current_state
                cpu = 75 + (anomaly_progress * 4) + np.random.normal(0, 2) 
                mem = 85 + (anomaly_progress * 2) + np.random.normal(0, 1) 
                net = 40 + np.random.normal(0, 5) # Network drops
                
                # Anomaly Logs
                logs.append({"timestamp": ts_str, "level": "WARN", "component": "memory", "message": "High memory usage detected. GC overhead limit."})
                
                if anomaly_progress >= 4:
                    logs.append({"timestamp": ts_str, "level": "ERROR", "component": "system", "message": "OutOfMemoryError: Java heap space."})

            # Cap values between 0 and 100
            cpu = min(max(cpu, 0.0), 100.0)
            mem = min(max(mem, 0.0), 100.0)
            net = max(net, 0.0)

            # -------------------------------------------------
            # WRITE DATA TO FILES (APPEND MODE)
            # -------------------------------------------------
            # Append Metrics
            append_csv("cpu_test.csv", [ts_str, "cpu_utilization_pct", round(cpu, 2), hostname], ["timestamp", "resource", "value", "hostname"])
            append_csv("mem_test.csv", [ts_str, "memory_utilization_pct", round(mem, 2), hostname], ["timestamp", "resource", "value", "hostname"])
            append_csv("net_test.csv", [ts_str, "network_io_mbit_sec", round(net, 2), hostname], ["timestamp", "resource", "value", "hostname"])

            # Append Logs
            with open("app_logs_test.log", "a") as f:
                for log in logs:
                    f.write(json.dumps(log) + "\n")

            # Console output so you can see what the generator is doing
            print(f"[{ts_str}] Wrote Log -> CPU: {cpu:.1f}%, Mem: {mem:.1f}% | State: {state}")

            # Sleep for 3 seconds before generating the next minute of data
            # (Change this to 60 if you want actual 1-minute intervals)
            time.sleep(3) 

        except KeyboardInterrupt:
            print("\n🛑 Generator stopped by user.")
            break
        except Exception as e:
            print(f"⚠️ Error generating data: {e}")
            time.sleep(2)


print("🧹 Wiping old test data for a clean run...")
files_to_delete = ['cpu_test.csv', 'mem_test.csv', 'net_test.csv', 'app_logs_test.log']

for file in files_to_delete:
    if os.path.exists(file):
        os.remove(file)
# Start generating
live_log_generator()
import pandas as pd
import numpy as np
import json
import math
import random
from datetime import datetime, timedelta

def generate_large_training_data():
    start_time = datetime(2026, 1, 1, 0, 0, 0)
    
    # 1. CHANGE THIS for more/less data (e.g., 30 days = 30 * 24 * 60)
    days_to_simulate = 7
    total_minutes = 12 # days_to_simulate * 24 * 60 
    hostname = "prod-web-srv-01"

    cpu_data, mem_data, net_data, logs = [], [], [], []

    # 2. Decide randomly when the 3 failures will happen
    # failure_start_times = random.sample(range(100, total_minutes - 60), 3)

    failure_start_times = random.sample(range(1, total_minutes), 1) # Test dataset 
    
    print(f"Generating {days_to_simulate} days of data...")
    print(f"Failures will occur at minutes: {sorted(failure_start_times)}")

    for i in range(total_minutes):
        current_time = start_time + timedelta(minutes=i)
        ts_str = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Create a "Daily Cycle" (peaks in the middle of the day, drops at night)
        time_of_day_multiplier = (math.sin(i * (2 * math.pi / 1440)) + 1) / 2 # Waves between 0 and 1

        # Check if we are currently inside a 30-minute failure window
        is_failing = False
        anomaly_progress = 0
        for f_start in failure_start_times:
            if f_start <= i < f_start + 30:
                is_failing = True
                anomaly_progress = i - f_start
                break

        # -------------------------------------------------
        # NORMAL BEHAVIOR (Fluctuates based on time of day)
        # -------------------------------------------------
        if not is_failing:
            # CPU fluctuates between 20% (night) and 60% (day)
            cpu = 20 + (40 * time_of_day_multiplier) + np.random.normal(0, 2)
            # Memory stays relatively stable, climbs slightly during the day
            mem = 40 + (20 * time_of_day_multiplier) + np.random.normal(0, 1)
            # Network drops low at night, high during day
            net = 100 + (600 * time_of_day_multiplier) + np.random.normal(0, 10)
            
            # Normal application logs (more logs during peak day hours)
            if random.random() < (0.2 + 0.5 * time_of_day_multiplier):
                logs.append({"timestamp": ts_str, "level": "INFO", "component": "system", "message": "Health check OK."})
            if i % 15 == 0:
                logs.append({"timestamp": ts_str, "level": "DEBUG", "component": "cache", "message": "Cache refreshed."})
                
        # -------------------------------------------------
        # FAILURE BEHAVIOR (Memory Leak & CPU Spike)
        # -------------------------------------------------
        else:
            # Metrics go crazy based on how long the failure has been happening (up to 30 mins)
            cpu = 70 + (anomaly_progress * 1.5) + np.random.normal(0, 2) 
            mem = 80 + (anomaly_progress * 1.0) + np.random.normal(0, 1) 
            net = 50 + np.random.normal(0, 5) # Network crashes down
            
            # Application logs start screaming
            logs.append({"timestamp": ts_str, "level": "WARN", "component": "memory", "message": "High memory usage detected. GC overhead limit."})
            
            # Final failure stages
            if anomaly_progress > 20:
                logs.append({"timestamp": ts_str, "level": "ERROR", "component": "system", "message": "OutOfMemoryError: Java heap space."})
                logs.append({"timestamp": ts_str, "level": "ERROR", "component": "network", "message": "Connection timeout - failed to serve request."})

        # Cap the values logically so they don't go below 0 or above 100
        cpu = min(max(cpu, 0.0), 100.0)
        mem = min(max(mem, 0.0), 100.0)
        net = max(net, 0.0)

        # Append to lists
        cpu_data.append([ts_str, "cpu_utilization_pct", round(cpu, 2), hostname])
        mem_data.append([ts_str, "memory_utilization_pct", round(mem, 2), hostname])
        net_data.append([ts_str, "network_io_mbit_sec", round(net, 2), hostname])

    # Save Metrics to CSV
    pd.DataFrame(cpu_data, columns=["timestamp", "resource", "value", "hostname"]).to_csv("cpu_test.csv", index=False)
    pd.DataFrame(mem_data, columns=["timestamp", "resource", "value", "hostname"]).to_csv("mem_test.csv", index=False)
    pd.DataFrame(net_data, columns=["timestamp", "resource", "value", "hostname"]).to_csv("net_test.csv", index=False)

    # Save Logs to JSON lines
    with open("app_logs_test.log", "w") as f:
        for log in logs:
            f.write(json.dumps(log) + "\n")
            
    print("✅ Successfully generated massive test datasets!")

# Run the generator
generate_large_training_data()
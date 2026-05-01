import pandas as pd 
from functools import reduce
from ReadLogs import readtestlogs,readtrainlogs

def processed_logs(logs,cpu,memory,network):
    
    # logs,cpu,memory,network = readtrainlogs()

    # conerting time to dattime format
    logs['timestamp'] = pd.to_datetime(logs['timestamp'])
    
    # Counting all logs in a minute 
    logs_count = logs.groupby(['timestamp','level'])['level'].count().unstack(fill_value=0).reset_index().copy()
    
    cpu['timestamp'] = pd.to_datetime(cpu['timestamp'])
    memory['timestamp'] = pd.to_datetime(memory['timestamp'])
    network['timestamp'] = pd.to_datetime(network['timestamp'])
    
    # Combining all metrics
    df = reduce(lambda left, right: pd.merge(left, right, on='timestamp', how='outer'), [cpu,memory,network])
    
    # Combining all metrics with logs
    final = pd.merge(df,logs_count, on='timestamp', how= 'outer')
    final.fillna(0, inplace=True)

    # Define the exact log columns your model expects
    expected_log_columns = ['DEBUG', 'ERROR', 'INFO', 'WARN']
    
    # Loop through and add any missing columns with a value of 0
    for col in expected_log_columns:
        if col not in final.columns:
            final[col] = 0
    
    return final

# logs,cpu,memory,network=readtestlogs()
# print(processed_logs(logs,cpu,memory,network))
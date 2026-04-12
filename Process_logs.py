import pandas as pd 
import numpy as np
from functools import reduce

def processed_logs():
    # Fetch logs
    logs = pd.read_json('app_logs_train.log',lines=True)
    
    # conerting time to dattime format
    logs['timestamp'] = pd.to_datetime(logs['timestamp'])
    
    # Counting all logs in a minute 
    logs_count = logs.groupby(['timestamp','level'])['level'].count().unstack(fill_value=0).reset_index().copy()
    
    #  Fetching only timestamp and value where value column name is changed to CPU,MEMORY,NETWORK resp
    cpu = pd.read_csv('cpu_train.csv').rename(columns={'value': 'cpu'})[['timestamp','cpu']]
    memory = pd.read_csv('mem_train.csv').rename(columns={'value': 'memory'})[['timestamp','memory']]
    network = pd.read_csv('net_train.csv').rename(columns={'value': 'network'})[['timestamp','network']]
    
    cpu['timestamp'] = pd.to_datetime(cpu['timestamp'])
    memory['timestamp'] = pd.to_datetime(memory['timestamp'])
    network['timestamp'] = pd.to_datetime(network['timestamp'])
    
    # Combining all metrics
    df = reduce(lambda left, right: pd.merge(left, right, on='timestamp', how='outer'), [cpu,memory,network])
    
    # Combining all metrics with logs
    final = pd.merge(df,logs_count, on='timestamp', how= 'outer')
    
    return final[['cpu','memory','network','DEBUG','ERROR','INFO','WARN']]

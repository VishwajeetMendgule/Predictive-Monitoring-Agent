import pandas as pd

def readtrainlogs():

    # Fetch logs
    logs = pd.read_json('app_logs_train.log',lines=True)

    #  Fetching only timestamp and value where value column name is changed to CPU,MEMORY,NETWORK resp
    cpu = pd.read_csv('cpu_train.csv').rename(columns={'value': 'cpu'})[['timestamp','cpu']]
    memory = pd.read_csv('mem_train.csv').rename(columns={'value': 'memory'})[['timestamp','memory']]
    network = pd.read_csv('net_train.csv').rename(columns={'value': 'network'})[['timestamp','network']]

    return logs,cpu,memory,network

def readtestlogs():
    logs = pd.read_json('D:/Preditictive Agent/app_logs_test.log',lines=True)

    #  Fetching only timestamp and value where value column name is changed to CPU,MEMORY,NETWORK resp
    cpu = pd.read_csv('D:/Preditictive Agent/cpu_test.csv').rename(columns={'value': 'cpu'})[['timestamp','cpu']]
    memory = pd.read_csv('D:/Preditictive Agent/mem_test.csv').rename(columns={'value': 'memory'})[['timestamp','memory']]
    network = pd.read_csv("D:/Preditictive Agent/net_test.csv").rename(columns={'value': 'network'})[['timestamp','network']]

    return logs,cpu,memory,network
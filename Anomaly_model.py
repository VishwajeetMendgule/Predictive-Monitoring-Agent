from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd
from Process_logs import processed_logs
import joblib

class Anomaly_model:
    def __init__(self):

     self.model = joblib.load('anomaly_model.pkl')
     self.scaler = joblib.load('data_scaler.pkl')

    def model_train(self,logs: pd.DataFrame):
        data = logs.values
        scaler = StandardScaler()
        model = IsolationForest(contamination=0.05, random_state=42)
    
        X_scaled = scaler.fit_transform(data)
        model.fit(X_scaled)
    
        joblib.dump(model, 'anomaly_model.pkl')
        joblib.dump(scaler, 'data_scaler.pkl')
        
        self.model = model
        self.scaler = scaler
    
    
    def an_model(self,logs: pd.DataFrame):
    
        log = logs.copy()
    
        X_scaled = self.scaler.transform(logs.values) 
        log['anomaly_score'] = self.model.decision_function(X_scaled)
        log['is_anomaly'] = self.model.predict(X_scaled)
    
        critical_anomalies = log[(log['is_anomaly'] == -1) & (log['ERROR'] > 0)]
        return critical_anomalies

m = Anomaly_model()
print(m.an_model(processed_logs()))
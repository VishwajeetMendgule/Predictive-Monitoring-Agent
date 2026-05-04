# 🚀 NeuroPulse – AIOps Predictive Monitoring Agent

## 📌 Overview

**NeuroPulse** is an AIOps-based predictive monitoring system designed to analyze application logs and system metrics in real time. It detects anomalies, predicts future system behavior, and provides AI-driven root cause analysis with actionable insights.

The system combines:
- Machine Learning (Anomaly Detection + LSTM Prediction)
- Real-time streaming (WebSockets)
- AI-powered diagnostics (LLM)
- Interactive dashboard (React)

---

## 🏗️ Architecture

The system is divided into three layers:

1. **Data Processing (Python)**
   - Log ingestion & preprocessing
   - Anomaly detection (Isolation Forest)
   - Prediction (LSTM)
   - AI root cause analysis

2. **Backend (Node.js + Express + Socket.IO)**
   - REST APIs for logs & metrics
   - Real-time telemetry streaming
   - SQLite database integration

3. **Frontend (React + Vite)**
   - Live monitoring dashboard
   - Log explorer
   - AI chat interface

---

## ⚙️ Prerequisites

Make sure you have installed:

- Python 3.9+
- Node.js (v18+ recommended)
- npm
- SQLite

---

## 📦 Installation

### 1️⃣ Clone Repository

```bash
git clone <your-repo-url>
cd <project-folder>
```

---

### 2️⃣ Backend Setup (Node.js)

```bash
cd backend
npm install
node server.js
```

---

### 3️⃣ Frontend Setup (React)

```bash
cd frontend
npm install
npm run dev
```

---

### 4️⃣ Python Setup (ML Pipeline)

```bash
pip install -r requirements.txt
```

---

## 🧠 Model Setup

⚠️ IMPORTANT: Update model paths before running

### Anomaly Model (Anomaly_model.py)

```python
self.model = joblib.load('path/to/anomaly_model.pkl')
self.scaler = joblib.load('path/to/data_scaler.pkl')
```

### LSTM Model (Prediction.py)

```python
model = load_model('path/to/lstm_model')
```

---

## 📂 Data File Configuration

Update file paths in:

**ReadLogs.py**

```python
logs = pd.read_json('data/app_logs_test.log', lines=True)
cpu = pd.read_csv('data/cpu_test.csv')
```

---

## 🔐 Environment Variables

Create a `.env` file:

```
apikey=YOUR_GROQ_API_KEY
ALERT_EMAIL=your_email@gmail.com
ALERT_APP_PASSWORD=your_app_password
```

---

## ▶️ Running the System

```bash
# Backend
cd backend
node server.js

# Frontend
cd frontend
npm run dev

# Python Pipeline
python Main.py
```

---

## 🔄 Data Flow

Logs + Metrics → Processing → Anomaly Detection → Prediction → AI Analysis → Alert → Dashboard

---

## 📊 Features

- Real-time monitoring dashboard  
- Anomaly detection using ML  
- Predictive analytics (LSTM)  
- AI-based root cause analysis  
- Email alerting system  
- Maintenance window handling  
- Log explorer  
- AI chat interface  

---

## ⚠️ Notes

- Update all file paths before running  
- Models must be pre-trained  
- Run backend before frontend  
- Python pipeline must run continuously  

---

## 🚀 Future Enhancements

- Kafka integration  
- Cloud deployment  
- Multi-service monitoring  

---

## 📄 License

For educational/demo purposes.

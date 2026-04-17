import requests
import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
# Intigrating HCL AI cafe 

def generate_answer(currentdata,futuredata,currentlogs):
    prompt = f"""Act as an AIOps SRE. Analyze the telemetry below to diagnose impending failures and root causes. 
    Output ONLY valid, raw JSON (no markdown, no backticks).

INPUTS:
Current System Metrics: {currentdata}
LSTM Predictions(Next 1-5 Mins): {futuredata}
Logs: {currentlogs}

SCHEMA:
{{
  "alert_severity": "CRITICAL" | "WARNING" | "STABLE",
  "impending_failure_type": "Brief failure name (e.g., JVM OutOfMemory)",
  "root_cause_analysis": "Concise root cause correlation. Maximum 2 sentences.",
  "estimated_time_to_impact_mins": <integer>,
  "recommended_remediation": "One immediate actionable step."
}}"""
    deploymentName = "gpt-4.1"
    apiVerion = "2024-12-01-preview"
    CHAT_MODEL_API = f"https://aicafe.hcl.com/AICafeService/api/v1/subscription/openai/deployments/{deploymentName}/chat/completions?api-version={apiVerion}"

    
    headers = {
        "Content-Type": "application/json",
        "api-key": os.getenv("api_Key")
    }

    payload = {
        "model": "gpt-4.1",
        "messages": [
            {
            "role": "user",
            "content": prompt
            }
        ],
        "maxTokens": 110,
        "temperature": 0
    }

    response = requests.post(url=CHAT_MODEL_API, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        print(f"Chat model error {response.status_code}: {response.text}")
        return None
    
# query = "Hey!"
# print(generate_answer(query))
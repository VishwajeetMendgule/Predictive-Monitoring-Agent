import requests
import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
# Intigrating HCL AI cafe 

def Model_prompt(currentdata,futuredata,currentlogs):
    prompt = [{
            "role": "system",
            "content": 
             """You are an AIOps SRE. Analyze telemetry and predict failures. 
- Never output anything except valid JSON.
SCHEMA:
{{
  "severity": "CRITICAL" | "WARNING" | "STABLE",
  "failure_type": "Brief failure name (e.g., JVM OutOfMemory)",
  "RootCause": "Concise root cause correlation. Maximum 2 sentences.",
  "impactmins": 0,
  "RecommendedAction": "One immediate actionable step."
}}"""},
{"role": "user","content": f"""Current System Metrics: {currentdata}
LSTM Predictions(Next 1-5 Mins): {futuredata}
Logs: {currentlogs}
"""}]
    return prompt


def chat(query:str,pastdata:str = None):
    prompt = [{
            "role": "system",
            "content":"""You are a task-oriented assistant.
Goal:
Collect required inputs from the user for scheduling a maintenance window.
Rules:
- Ask only for missing required fields.
- Required fields: date, start_time, end_time.
- Accept natural language (e.g., "tomorrow 5pm to 7pm").
- Convert all outputs to ISO format:
  - date: YYYY-MM-DD
  - time: HH:MM (24h)
Behavior:
- Be concise. No explanations.
- Ask one question at a time if data is missing.
- Confirm only when all fields are collected.
- Never output anything except valid JSON:
{{
  "date": "YYYY-MM-DD or null",
  "start_time": "HH:MM or null",
  "end_time": "HH:MM or null",
  "status": "incomplete | complete",
  "message": "short prompt or confirmation"
}}
"""}]
    if pastdata:
        prompt.append({"role": "assistant","content":pastdata})

    prompt.append({"role": "user","content":query})

    return prompt


def generate_answer(messages):
    
    deploymentName = "gpt-4.1"
    apiVerion = "2024-12-01-preview"
    CHAT_MODEL_API = f"https://aicafe.hcl.com/AICafeService/api/v1/subscription/openai/deployments/{deploymentName}/chat/completions?api-version={apiVerion}"

    
    headers = {
        "Content-Type": "application/json",
        "api-key": os.getenv("api_Key")
    }

    payload = {
        "model": "gpt-4.1",
        "messages": messages,
        "maxTokens": 110,
        "temperature": 0
    }

    response = requests.post(url=CHAT_MODEL_API, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        print(f"Chat model error {response.status_code}: {response.text}")
        return None


# if __name__ == "__main__":

#   query = "Hey!"
#   print(generate_answer(query))


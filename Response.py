import requests
import os
from datetime import datetime
from dotenv import find_dotenv, load_dotenv
import json
from reponsemodel import get_response
from DB_query import save_chat_message, get_chat_history, add_maintenance_window

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

def chat(query: str, history_messages: list = None):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M (24h)")
    prompt = [{
            "role": "system",
            "content":f"""You are a task-oriented assistant.
Goal:
Collect required inputs from the user for scheduling a maintenance window.
Current System Time: {current_time}
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
  "reason": "extracted reason" or null,
  "status": "incomplete | complete",
  "message": "your reply asking for the next missing field, or confirming success"
}}
"""}]
    if history_messages:
        # Preserve prior turns so the model remembers the last question and user answer
        prompt.extend(history_messages)

    prompt.append({"role": "user","content":query})

    return prompt


def extract_json_object(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find('{')
        end = text.rfind('}')
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                pass
    return None


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

def handle_maintenance_chat(user_input, session_id):
    """
    Handles the maintenance window scheduling chat.
    Saves chat history and inserts maintenance window when complete.
    
    Parameters:
    - user_input: The user's message
    - session_id: Unique session identifier
    
    Returns:
    - Assistant's response message
    """
    # Get full past chat history
    history = get_chat_history(session_id)
    history_messages = []
    if history:
        history_messages = [{"role": role, "content": content} for role, content in history]

    # Save user message
    save_chat_message(session_id, 'user', user_input)

    # Generate prompt
    prompt = chat(user_input, history_messages)

    # Get LLM response
    # response = generate_answer(prompt)
    response = get_response(prompt)
    
    if response:
        # Save assistant message
        save_chat_message(session_id, 'assistant', response)
        
        # Parse the response to check if complete
        data = extract_json_object(response)
        if not data:
            return "Error parsing response. Please try again."

        if data.get('status') == 'complete':
            # Insert maintenance window
            date = data['date']
            start_time = data['start_time']
            end_time = data['end_time']
            reason = data.get('reason', 'Scheduled maintenance')
            
            # Combine date and times
            start_datetime = f"{date} {start_time}:00"
            end_datetime = f"{date} {end_time}:00"
            
            add_maintenance_window(start_datetime, end_datetime, reason)
            
            return f"Maintenance window scheduled successfully: {start_datetime} to {end_datetime} - {reason}"
        else:
            return data.get('message', 'Please provide the required information.')
    else:
        return "Error communicating with AI. Please try again."


# print(get_response(chat("Schedule maintenance for tomorrow from 5pm to 7pm due to security patching.")))

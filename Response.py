import requests
import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
# Intigrating HCL AI cafe 

def generate_answer(query):
    PROMPT_TEMPLATE = """
You are an intelligent Predictive Monitoring system specialized in analyzing Application Logs.

Your task is to analyze the logs, Predicyed values by LSTM and give proper reasigionig for the future failure.

If the input is **not** a movie review, respond with the exact JSON below:

---
### INPUT QUERY
"{user_query}"
---

### TASK OBJECTIVES
1. Determine the **overall sentiment** as one of: Positive, Negative, Neutral, or Mixed.  
2. Estimate the **sentiment intensity** on a scale of 1-5 (1 = very weak, 5 = very strong).  
3. Identify the **dominant emotion** (e.g., happiness, anger, frustration, sadness, excitement, gratitude).  
4. Detect the **subject or target** of sentiment, if any (e.g., movie title, actor, director, scene).  
5. Provide a **brief reasoning** explaining why that sentiment was chosen.  
6. Output the result strictly in the JSON format shown below.

---

### OUTPUT FORMAT (JSON)
{{
  "sentiment": "<Positive | Negative | Neutral | Mixed>",
  "intensity": "<1-5>",
  "dominant_emotion": "<emotion>",
  "target": "<what the sentiment is about, or 'None'>",
  "reasoning": "<brief explanation in 1-2 sentences>"
}}

---

### INSTRUCTIONS
- Analyze only movie reviews; reject any non-movie review input as described above.  
- Be precise and consistent.  
- Base sentiment strictly on the language used — not assumptions.  
- Avoid moral judgments or opinions.  
- Do not include any text outside the JSON.  
"""
    prompt = PROMPT_TEMPLATE.format(user_query=query)
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
        "maxTokens": 100,
        "temperature": 0
    }

    response = requests.post(url=CHAT_MODEL_API, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        print(f"Chat model error {response.status_code}: {response.text}")
        return None
    
query = "Hey!"
print(generate_answer(query))
from groq import Groq
import os
from dotenv import find_dotenv, load_dotenv
 
load_dotenv(find_dotenv())
 
client = Groq(api_key=os.getenv("apikey"))
 
def get_response(prompt):
    try:
         completion = client.chat.completions.create(
         messages= prompt,
         model="llama-3.3-70b-versatile",
         max_tokens=70,
         temperature=0.7,
         top_p=1,
         stream=True,
         stop=None
         )
         reply = ''
         for chunk in completion:
             if chunk.choices[0].delta.content:
                 reply += chunk.choices[0].delta.content
         reply = reply.replace("</s>","")
         return reply.strip()
 
    except Exception as  e:
          return e
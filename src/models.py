import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False
#getting environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OLLAMA_MODEL=os.getenv("OLLAMA_MODEL")

#generate answer from openai api
def generate_openai(prompt: str, model: str = "gpt-4o", max_tokens: int = 512,chat_memory:bool =False, summary:str ="this is the user's first message"):
    if OPENAI_AVAILABLE and OPENAI_API_KEY:
        client = OpenAI(
        api_key=OPENAI_API_KEY,base_url="https://api.metisai.ir/openai/v1"
        )
           
    if not OPENAI_AVAILABLE:
        raise RuntimeError("openai package unavailable")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role":"user", "content":  prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
            stream=True,
            )
        return response
    except Exception as e:
        try:
            
            resp= client.chat.completions.create(
                model=model,
                messages=[{"role":"user", "content":  prompt}],
                max_tokens=max_tokens,
                temperature=0.7,
                stream=True,
                )
            return resp
        except Exception as e2:
            raise RuntimeError(f"OpenAI call failed: {e} | {e2}")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

#generate answer from ollama api
def generate_ollama(prompt: str, model_name: str = OLLAMA_MODEL, stream: bool = True):
    url = f"{OLLAMA_HOST.rstrip('/')}/api/generate"
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": stream
    }
    headers = {"Content-Type": "application/json"}
    r = requests.post(url, json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    resp=[]
    #turn response to a stream
    for line in r.iter_lines(decode_unicode=True):
        if line:
            try:
                data = json.loads(line)
                
                if "response" in data:
                    resp.append(str(data["response"]))
                elif "output" in data:
                    resp.append(str(data["output"]))
            except json.JSONDecodeError:
                return json.JSONDecodeError
    return resp           
    

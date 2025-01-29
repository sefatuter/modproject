import requests
import re
import os
from dotenv import load_dotenv
load_dotenv()

OPENUI_API_URL = "http://localhost:3000/api/chat/completions"
OPENUI_API_KEY = os.getenv("OPENUI_API_KEY")
HEADERS = {"Authorization": f"Bearer {OPENUI_API_KEY}", "Content-Type": "application/json"}


def generate_rule_deepseek_rag(prompt):
    DATA = {
        "model": "modproject",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(OPENUI_API_URL, headers=HEADERS, json=DATA)

    # print(response)
    # print(response.json())

    if response.status_code == 200:
        response_json = response.json()
        
        # Extract the content part from the assistant's message
        content = response_json.get("choices", [])[0].get("message", {}).get("content", "")

        content = re.sub(r"<think>.*?</think>\n*", "", content, flags=re.DOTALL).strip()

        print(content)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        
    return content
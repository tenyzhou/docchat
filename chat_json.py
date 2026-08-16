import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")

resp = requests.post(
    "https://api.deepseek.com/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "从这句话里提取信息，只输出 JSON，不要任何其他文字，格式：{\"日期\": \"\", \"人名\": \"\", \"地点\": \"\"}。句子：张三于2026年8月16日在北京开会。"}
        ],
    },
    timeout=60,
)

content = resp.json()["choices"][0]["message"]["content"]
print("AI 返回的原文：", content)

data = json.loads(content)
print("解析后的字典：", data)
print("人名是：", data["人名"])
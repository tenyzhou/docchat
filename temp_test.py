import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")

def ask(question, temperature):          # 定义一个函数：传入问题和温度，返回 AI 回答
    resp = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": question}],
            "temperature": temperature,   # ★今天的主角
        },
        timeout=60,
    )
    return resp.json()["choices"][0]["message"]["content"]

question = "给我编一句广告词，介绍一杯柠檬水"

print("=== temperature = 0（冷：保守，几乎每次一样）===")
for i in range(3):
    print(f"第{i+1}次：", ask(question, 0))

print()
print("=== temperature = 1.5（热：放飞，每次不一样）===")
for i in range(3):
    print(f"第{i+1}次：", ask(question, 1.5))
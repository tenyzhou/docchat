import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")

# ★概念3：角色。system 是给模型设定身份和规则的
messages = [
    {"role": "system", "content": "你是一个只会用不超过三个字回答问题的怪人。"},
]

while True:                                   # 无限循环，直到用户输入 exit
    user_input = input("你（输入 exit 退出）：")
    if user_input == "exit":
        break
    messages.append({"role": "user", "content": user_input})   # 把用户的话加进历史

    resp = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": "deepseek-chat", "messages": messages},   # ★概念2：把整个历史都发给模型
        timeout=60,
    )
    result = resp.json()
    answer = result["choices"][0]["message"]["content"]
    print("AI：", answer)

    messages.append({"role": "assistant", "content": answer})    # 把 AI 的话也加进历史

    usage = result["usage"]                                      # ★概念1：token
    print(f"本轮累计花 {usage['total_tokens']} token")
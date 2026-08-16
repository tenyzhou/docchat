import os
import requests
from dotenv import load_dotenv

load_dotenv()                                     # 读 .env 文件
API_KEY = os.getenv("DEEPSEEK_API_KEY")           # 取出 key

resp = requests.post(                             # 发请求到 DeepSeek
    "https://api.deepseek.com/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",     # 出示身份凭证
        "Content-Type": "application/json",
    },
    json={
        "model": "deepseek-chat",                 # 用哪个模型
        "messages": [                             # 对话内容
            {"role": "user", "content": "你好，请用一句话介绍你自己"}
        ],
    },
    timeout=60,
)

print(resp.status_code)              # 200 = 成功
result = resp.json()                 # resp.json()函数：把服务器返回的JSON字符串解析成Python的字典
print(result["choices"][0]["message"]["content"]) # 取出 AI 的回答
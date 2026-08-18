import json
import os
import random

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")

random.seed(42)

# 1. 加载数据 + 抽样 100 题（和之前同一批）
with open("data/cmrc2018_dev.json", encoding="utf-8") as f:
    data = json.load(f)

docs = []
qas = []
seen = {}
for article in data["data"]:
    for p in article["paragraphs"]:
        ctx = p["context"]
        if ctx not in seen:
            seen[ctx] = len(docs)
            docs.append(ctx)
        idx = seen[ctx]
        for qa in p["qas"]:
            qas.append((qa["question"], idx))

sample = random.sample(qas, 100)

# 2. 用 DeepSeek 改写问题
def rewrite(question):
    prompt = (
        "把下面这个问题改写成：意思完全一样、但表达方式完全不同的问题。"
        "要求：不要使用原句中的实词（人名、作品名等专有名词除外），换个说法提问。"
        "只输出改写后的问题，不要任何其他文字。\n原问题：" + question
    )
    resp = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    return resp.json()["choices"][0]["message"]["content"]

# 3. 改写并保存
hard = []
for i, (question, gold_idx) in enumerate(sample):
    new_q = rewrite(question)
    hard.append({"question": new_q, "gold_idx": gold_idx})
    print(f"[{i+1}/100] 原：{question}\n          改：{new_q}")

with open("data/hard_set.json", "w", encoding="utf-8") as f:
    json.dump(hard, f, ensure_ascii=False, indent=2)

print("\n已保存 data/hard_set.json（100 道难题）")

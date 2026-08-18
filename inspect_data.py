import json

with open("data/cmrc2018_dev.json", encoding="utf-8") as f:
    data = json.load(f)          # JSON 字符串 → 字典（又是它）

articles = data["data"]          # 文章列表
print("文章数：", len(articles))

total_q = 0
for article in articles:         # 遍历每篇文章
    for p in article["paragraphs"]:   # 遍历每段
        total_q += len(p["qas"])      # 累计问题数
print("总问题数：", total_q)

# 看第一个例子
first = articles[0]
first_p = first["paragraphs"][0]
print("\n=== 第一篇文章标题 ===")
print(first["title"])
print("\n=== 第一段原文（前 100 字）===")
print(first_p["context"][:100])
print("\n=== 第一个问题 ===")
qa = first_p["qas"][0]
print("问题：", qa["question"])
print("标准答案：", qa["answers"][0]["text"])
import json
import random

import jieba
from rank_bm25 import BM25Okapi

random.seed(42)   # 固定随机种子，保证每次跑结果一样（可复现！）

# 1. 加载真实数据
with open("data/cmrc2018_dev.json", encoding="utf-8") as f:
    data = json.load(f)

# 2. 建语料库：每个"段落"是一篇文档；记录每道题的"正确答案段落"编号
docs = []          # 所有段落文本
qas = []           # 所有 (问题, 正确段落编号)
seen = {}
for article in data["data"]:
    for p in article["paragraphs"]:
        ctx = p["context"]
        if ctx not in seen:           # 去重
            seen[ctx] = len(docs)
            docs.append(ctx)
        idx = seen[ctx]
        for qa in p["qas"]:
            qas.append((qa["question"], idx))

print("语料库段落数：", len(docs))
print("问题总数：", len(qas))

# 3. 抽样 100 个问题（保证速度快，正式版再全量）
sample = random.sample(qas, 100)

# 4. 中文分词 + 建 BM25 索引
tokenized_docs = [list(jieba.cut(d)) for d in docs]
bm25 = BM25Okapi(tokenized_docs)

# 5. 逐个问题检索，算 Recall@5
hits = 0
for question, gold_idx in sample:
    query_tokens = list(jieba.cut(question))
    top5 = bm25.get_top_n(query_tokens, docs, n=5)   # 返回最相关的 5 段
    if docs[gold_idx] in top5:                        # 正确答案段落有没有进前 5
        hits += 1

recall = hits / len(sample)
print(f"\n🎯 第一个真实数字：Recall@5 = {hits}/{len(sample)} = {recall:.2%}")
import json
import os
import random

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"   # 国内镜像下载模型

import numpy as np
from sentence_transformers import SentenceTransformer

random.seed(42)   # 和 BM25 版同一个 seed → 同一批 100 题 → 公平对比！

# 1. 加载数据（和 BM25 版完全一样）
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

sample = random.sample(qas, 100)   # 同一批 100 题

# 2. 加载 embedding 模型（第一次自动下载 BGE 模型，约 100MB）
model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

# 3. 把 3219 段全部变成向量（第一次会慢，1-3 分钟正常）
print("正在把全部段落变成向量...")
doc_vecs = model.encode(docs, show_progress_bar=True)   # 形状 (3219, 512)

# 4. 逐题检索
def top5_index(qvec, doc_vecs):
    """返回相似度最高的 5 个段落下标。余弦相似度 = 点积 / (长度乘积)。"""
    qnorm = np.linalg.norm(qvec)                          # 问题向量的长度
    sims = (doc_vecs @ qvec) / (np.linalg.norm(doc_vecs, axis=1) * qnorm)  # 和每段的相似度
    return np.argsort(sims)[-5:][::-1]                    # 取最高的 5 个下标，从高到低

hits = 0
for question, gold_idx in sample:
    qvec = model.encode(question)                          # 问题也变成向量
    top5 = top5_index(qvec, doc_vecs)
    if gold_idx in top5:
        hits += 1

print(f"\n🎯 向量检索 Recall@5 = {hits}/{len(sample)} = {hits/len(sample):.2%}")
print("对比：BM25 是 97%")
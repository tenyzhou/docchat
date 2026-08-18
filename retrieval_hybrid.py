import json
import os
import random

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import numpy as np
import jieba
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

random.seed(42)

# 1. 数据（和之前完全一样，同一批 100 题）
with open("data/cmrc2018_dev.json", encoding="utf-8") as f:
    data = json.load(f)

docs, qas, seen = [], [], {}
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

# 2. BM25 索引
tokenized_docs = [list(jieba.cut(d)) for d in docs]
bm25 = BM25Okapi(tokenized_docs)

# 3. 向量
model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
doc_vecs = model.encode(docs, show_progress_bar=True)
doc_norms = np.linalg.norm(doc_vecs, axis=1)

def bm25_rank(qtokens):
    scores = bm25.get_scores(qtokens)          # 每段的 BM25 分数
    return np.argsort(scores)[-20:][::-1]      # 前 20 名的下标（从高到低）

def vec_rank(qvec):
    sims = (doc_vecs @ qvec) / (doc_norms * np.linalg.norm(qvec))
    return np.argsort(sims)[-20:][::-1]        # 前 20 名的下标（从高到低）

def fuse(rank1, rank2, top_k=20):
    """把两个排名折成分数相加：第1名20分，第2名19分……"""
    points = {}
    for rank, idx in enumerate(rank1):
        points[idx] = points.get(idx, 0) + (top_k - rank)
    for rank, idx in enumerate(rank2):
        points[idx] = points.get(idx, 0) + (top_k - rank)
    return sorted(points, key=points.get, reverse=True)[:5]   # 总分前 5

# 4. 混合检索评测
hits = 0
for question, gold_idx in sample:
    top5 = fuse(bm25_rank(list(jieba.cut(question))), vec_rank(model.encode(question)))
    if gold_idx in top5:
        hits += 1

print(f"\n混合检索 Recall@5 = {hits}/100 = {hits/100:.2%}")
print("对比：BM25 = 97% | 向量 = 95%")
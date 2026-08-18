import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"   # 国内镜像，下载模型更快；能直连就不用这行

from sentence_transformers import SentenceTransformer

# 加载中文嵌入模型（第一次会自动下载约 100MB，慢一点正常）
model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

# 三句话，测语义相似度
s1 = "今天北京天气怎么样"
s2 = "北京今天天气如何"       # 字面不同，意思一样
s3 = "这家店的菜很好吃"       # 完全无关

v1 = model.encode(s1)
v2 = model.encode(s2)
v3 = model.encode(s3)

print("向量的形状：", v1.shape)      # 比如 (512,)，一句话变成 512 个数字

def cos(a, b):                        # 余弦相似度
    return float(a @ b / ((a @ a) ** 0.5 * (b @ b) ** 0.5))

print("s1 vs s2（意思一样，字面不同）：", cos(v1, v2))   # 应该很高，比如 0.8+
print("s1 vs s3（完全无关）：", cos(v1, v3))             # 应该很低，比如 0.3
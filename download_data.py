import os
import requests

os.makedirs("data", exist_ok=True)     # 确保 data 文件夹存在

url = "https://raw.githubusercontent.com/ymcui/cmrc2018/master/squad-style-data/cmrc2018_dev.json"
resp = requests.get(url, timeout=60)
print("状态码：", resp.status_code)

with open("data/cmrc2018_dev.json", "w", encoding="utf-8") as f:
    f.write(resp.text)

print("已保存，字符数：", len(resp.text))
"""下载的 cmrc2018_dev.json 是 CMRC 2018 数据集的验证集（dev set）。
CMRC 2018 = 中文机器阅读理解数据集，由哈工大讯飞联合实验室等单位组织（中文机器阅读理解评测用的就是它）
内容是什么：一批真实的中文百科文章（类似维基百科的词条）。你看到的第一篇是《战国无双3》——就是一篇介绍这个游戏的文章。
GitHub 上官方仓库 ymcui/cmrc2018 的 squad-style-data 文件夹里的 cmrc2018_dev.json。
所以它是有出处的、学术界公认的数据集，不是网上随便找的"""
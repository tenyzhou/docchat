#1读文件
f = open("article.txt", encoding="utf-8") #open是内置函数可以直接打开，里面有中文内容必须指定编码
content = f.read()  #读文件f存入变量content
f.close()   #用完关掉文件（好习惯，省资源）

#2去标点
for ch in "，。！？,.!?；：":
    content = content.replace(ch," ")   #replace把变量ch中的内容替换成空格

#3分词
words = content.split()     #split 是字符串的方法,只能挂在字符串后面用点调用,按空格切分后返回列表

#4统计每个词的次数
counts = {}
for word in words:
    counts[word] = counts.get(word,0) + 1

#5排序
sorted_words = sorted(counts.items(),key=lambda x: x[1],reverse=True)
#把字典counts变成键值对，每项是 (词, 次数)，告诉 sorted"按每对的第 2 个元素（次数）排序"
#lambda是个匿名小函数，x代表每个键值对，x[1]取它的次数，就是取键值对里面的值，第二个所以是x[1],第一个是x[0]
#reverse逆置排序，不写（默认）→ 从小到大

#6. 写入 output.txt ← 新东西②
out = open("output.txt", "w", encoding="utf-8")#第二个位置w是写入
for word, num in sorted_words:
    out.write(f"{word} {num}\n")
out.close()

print("完成！请打开 output.txt 看结果")
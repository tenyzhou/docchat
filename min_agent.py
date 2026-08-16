import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"


def chat(messages, tools):
    """调用模型。messages 是对话历史，tools 是工具描述列表。"""
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": tools,              # 告诉模型：你有哪些工具可用
        "tool_choice": "auto",       # 让模型自己决定用不用
    }
    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]


# ============ 工具：模型"决定"，你的代码"执行" ============
def get_weather(city):
    return f"{city} 今天晴，25 度"


def calculator(expr):
    allowed = set("0123456789+-*/（）(). ")
    if not all(ch in allowed for ch in expr):
        return "错误：表达式含非法字符"
    try:
        return str(eval(expr, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"错误：{e}"


# ============ 工具描述：告诉模型有哪些工具、怎么用 ============
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询某个城市的天气。当用户问天气时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名，例如 北京"},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式。当用户需要算数时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expr": {"type": "string", "description": "数学表达式，例如 (3+5)*2"},
                },
                "required": ["expr"],
            },
        },
    },
]


# ============ 工具分发：根据模型的选择，执行对应的函数 ============
def call_tool(name, args):
    if name == "get_weather":
        return get_weather(args["city"])
    if name == "calculator":
        return calculator(args["expr"])
    return "错误：没有这个工具"


# ============ 主循环：Agent 的心脏（重点看这里）============
def run_agent(user_question, max_turns=5):
    messages = [{"role": "user", "content": user_question}]

    for turn in range(max_turns):          # 最多循环 max_turns 轮
        print(f"\n===== 第 {turn + 1} 轮 =====")

        msg = chat(messages, TOOLS)        # 让模型"想"一步
        print("模型输出：", json.dumps(msg, ensure_ascii=False)[:200])

        if msg.get("tool_calls"):          # 情况A：模型决定用工具
            messages.append(msg)           # ① 把模型这条"决定"存进历史
            for tc in msg["tool_calls"]:   # ② 逐个执行工具
                name = tc["function"]["name"]
                args = json.loads(tc["function"]["arguments"])   # JSON 字符串 → 字典
                result = call_tool(name, args)                   # 执行！你的代码干活
                print(f"→ 执行工具 {name}，参数 {args}，结果：{result}")
                messages.append({          # ③ 把工具结果存进历史
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })
            continue                       # ④ 让模型看到结果，再想一轮

        else:                              # 情况B：模型直接回答
            print("AI 最终回答：", msg["content"])
            break                          # 任务完成，退出循环

    else:
        print("\n达到最大轮数，强制停止")


if __name__ == "__main__":
    run_agent("北京天气怎么样？")
    run_agent("帮我算一下 (3 + 5) * 2 等于多少")
    run_agent("你好，简单自我介绍一下")
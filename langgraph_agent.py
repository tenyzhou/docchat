import json
import operator
import os
import requests
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"


def chat(messages, tools):
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
    }
    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]


def get_weather(city):
    return f"{city} 今天晴，25 度"


def calculator(expr):
    allowed = set("0123456789+-*/(). ")     # 已修复：加上括号
    if not all(ch in allowed for ch in expr):
        return "错误：表达式含非法字符"
    try:
        return str(eval(expr, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"错误：{e}"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询某个城市的天气。当用户问天气时调用。",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "城市名，例如 北京"}},
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
                "properties": {"expr": {"type": "string", "description": "数学表达式，例如 (3+5)*2"}},
                "required": ["expr"],
            },
        },
    },
]


def call_tool(name, args):
    if name == "get_weather":
        return get_weather(args["city"])
    if name == "calculator":
        return calculator(args["expr"])
    return "错误：没有这个工具"


# ================= LangGraph：把昨天的循环画成图 =================
class State(TypedDict):
    messages: Annotated[list, operator.add]   # 状态 = 消息历史；add 表示新消息追加


def agent_node(state):
    """节点 1：让模型想一步。返回新增的消息。"""
    msg = chat(state["messages"], TOOLS)
    return {"messages": [msg]}


def tools_node(state):
    """节点 2：执行模型要求的工具。返回新增的工具结果。"""
    last = state["messages"][-1]
    results = []
    for tc in last["tool_calls"]:
        name = tc["function"]["name"]
        args = json.loads(tc["function"]["arguments"])
        result = call_tool(name, args)
        print(f"→ 执行工具 {name}，参数 {args}，结果：{result}")
        results.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
    return {"messages": results}


def should_continue(state):
    """条件边：看模型最后一条消息有没有要求用工具。"""
    last = state["messages"][-1]
    if last.get("tool_calls"):
        return "tools"       # 要去执行工具
    return END               # 否则结束


graph = StateGraph(State)
graph.add_node("agent", agent_node)                              # 节点1：模型思考
graph.add_node("tools", tools_node)                              # 节点2：执行工具
graph.set_entry_point("agent")                                   # 从"思考"进入
graph.add_conditional_edges("agent", should_continue,
                            {"tools": "tools", END: END})       # 思考完看情况跳转
graph.add_edge("tools", "agent")                                 # 执行完回到思考

app = graph.compile()                                            # 编译成可运行程序
print(app.get_graph().draw_ascii())    # 把图打印出来看！
if __name__ == "__main__":
    result = app.invoke({"messages": [{"role": "user",
                                       "content": "北京天气怎么样？顺便算一下 (3+5)*2"}]})
    print("\n最终回答：", result["messages"][-1]["content"])

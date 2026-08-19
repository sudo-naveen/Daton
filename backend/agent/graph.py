import json
import logging
from typing import Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import backend.config as config
from backend.agent.state import AgentState
from backend.agent.prompts import SYSTEM_PROMPT
from backend.tools.sql_tool import sql_tool, get_database_schema
from backend.tools.rag_tool import rag_search
from backend.tools.python_tool import analyze_data
from backend.tools.visualization_tool import create_chart
from backend.tools.calculator_tool import calculator

logger = logging.getLogger("daton.agent")


_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=config.GEMINI_API_KEY,
            max_tokens=4096,
            request_timeout=180,
        )
    return _llm


tools = [sql_tool, get_database_schema, rag_search, analyze_data, create_chart, calculator]
tool_map = {t.name: t for t in tools}


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts).strip()
    return str(content)


def call_model(state: AgentState):
    llm = get_llm()
    llm_with_tools = llm.bind_tools(tools)

    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    try:
        response = llm_with_tools.invoke(messages)
        response.content = _extract_text(response.content)
    except Exception as e:
        logger.error("LLM call failed: %s", e)
        err_msg = str(e)
        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
            response = AIMessage(content="API rate limit reached. Please wait ~60 seconds and try again.")
        else:
            response = AIMessage(content=f"I encountered an error communicating with the AI model: {err_msg}")
    return {"messages": [response], "active_tools": []}


def call_tool(state: AgentState):
    last_message = state["messages"][-1]
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {"messages": [], "active_tools": []}

    results = []
    active_tools = []
    tool_messages = []

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        active_tools.append(tool_name)

        if tool_name in tool_map:
            try:
                logger.info("Calling tool: %s with args: %s", tool_name, tool_args)
                result = tool_map[tool_name].invoke(tool_args)
                results.append({"tool": tool_name, "result": result, "status": "success"})
                logger.info("Tool %s returned %d chars", tool_name, len(str(result)))
            except Exception as e:
                logger.error("Tool %s failed: %s", tool_name, e)
                result = f"Error executing {tool_name}: {str(e)}"
                results.append({"tool": tool_name, "result": result, "status": "error"})
        else:
            result = f"Unknown tool: {tool_name}"
            results.append({"tool": tool_name, "result": result, "status": "error"})

        tool_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
            )
        )

    return {
        "messages": tool_messages,
        "tool_results": state.get("tool_results", []) + results,
        "active_tools": active_tools,
    }


def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


def create_graph():
    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", call_tool)

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()


_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = create_graph()
    return _graph


def run_agent(
    user_message: str,
    messages: list = None,
    session_id: str = "default",
    context: dict = None,
) -> dict:
    graph = get_graph()

    if messages is None:
        messages = []

    state: AgentState = {
        "messages": messages + [HumanMessage(content=user_message)],
        "tool_results": [],
        "context": context or {},
        "session_id": session_id,
        "rag_sources": [],
        "sql_query": None,
        "chart_data": None,
        "active_tools": [],
    }

    final_state = graph.invoke(state)

    ai_response = None
    for msg in reversed(final_state["messages"]):
        if isinstance(msg, AIMessage) and not msg.tool_calls:
            ai_response = msg.content
            break

    if ai_response is None:
        ai_response = "I was unable to generate a response. Please try again."

    sources = []
    for tr in final_state.get("tool_results", []):
        if tr.get("tool") == "rag_search" and tr.get("status") == "success":
            try:
                result_text = tr["result"]
                if "[Result" in result_text:
                    parts = result_text.split("[Result")
                    for part in parts[1:]:
                        lines = part.strip().split("\n")
                        for line in lines:
                            if line.startswith("Source:"):
                                sources.append(line.replace("Source:", "").strip())
            except Exception:
                pass

    chart_path = None
    for tr in final_state.get("tool_results", []):
        if tr.get("tool") == "create_chart" and tr.get("status") == "success":
            try:
                chart_info = json.loads(tr["result"])
                chart_path = chart_info.get("chart_path")
            except Exception:
                pass

    used_tools = []
    for msg in final_state["messages"]:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                used_tools.append(tc["name"])

    return {
        "response": ai_response,
        "sources": list(set(sources)),
        "chart_path": chart_path,
        "tools_used": list(set(used_tools)),
        "tool_results": final_state.get("tool_results", []),
        "messages": final_state["messages"],
    }

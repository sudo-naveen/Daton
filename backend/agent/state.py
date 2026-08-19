from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    tool_results: List[Dict[str, Any]]
    context: Dict[str, Any]
    session_id: str
    rag_sources: List[Dict[str, Any]]
    sql_query: Optional[str]
    chart_data: Optional[Dict[str, Any]]
    active_tools: List[str]

from typing import Annotated
from langchain_aws import ChatBedrockConverse
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict
from langchain_community.tools.tavily_search import TavilySearchResults


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in the case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    return {"messages": [model.invoke(state["messages"])]}


tool = TavilySearchResults(max_results=2)
tools = [tool]
tool_node = ToolNode(tools=[tool])

model = ChatBedrockConverse(
    model="anthropic.claude-3-haiku-20240307-v1:0").bind_tools(tools)

# Construct graph
graph_builder = StateGraph(State)

# Add nodes
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)
# Add edges
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)

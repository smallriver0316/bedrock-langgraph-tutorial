import json
from typing import Annotated
from langchain_aws import ChatBedrockConverse
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import ToolMessage
from typing_extensions import TypedDict
from langchain_community.tools.tavily_search import TavilySearchResults


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in the case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


# class BasicToolNode:
#     def __init__(self, tools: list) -> None:
#         self.tools_by_name = {tool.name: tool for tool in tools}

#     def __call__(self, inputs: list) -> None:
#         if messages := inputs.get("messages", []):
#             message = messages[-1]
#         else:
#             raise ValueError("No message found in input")

#         outputs = []
#         for tool_call in message.tool_calls:
#             tool_result = self.tools_by_name[tool_call["name"]].invoke(
#                 tool_call["args"])
#             outputs.append(
#                 ToolMessage(
#                   content=json.dumps(tool_result),
#                   name=tool_call["name"],
#                   tool_call_id=tool_call["id"],
#                 )
#             )
#         return {"messages": outputs}


graph_builder = StateGraph(State)

tool = TavilySearchResults(max_results=2)
tools = [tool]
model = ChatBedrockConverse(
    model="anthropic.claude-3-haiku-20240307-v1:0").bind_tools(tools)


def chatbot(state: State):
    return {"messages": [model.invoke(state["messages"])]}


# def route_tools(state: State):
#     if isinstance(state, list):
#         ai_message = state[-1]
#     elif messages := state.get("messages", []):
#         ai_message = messages[-1]
#     else:
#         raise ValueError(
#             f"No messages found in input state to tool_edge: {
#                 state
#             }")

#     if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
#         return "tools"

#     return END


# tool_node = BasicToolNode(tools=[tool])
tool_node = ToolNode(tools=[tool])

# Add nodes
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)
# Add edges
graph_builder.add_edge(START, "chatbot")
# graph_builder.add_conditional_edges(
#     "chatbot",
#     route_tools,
#     {"tools": "tools", END: END}
# )
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()


def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            print("Assistant", value["messages"][-1].content)


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        stream_graph_updates(user_input)
    except Exception:
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break

from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage
from graph_builder import graph_builder


def stream_graph_updates(graph: CompiledStateGraph, config, user_input):
    for event in graph.stream(
            user_input,
            config,
            stream_mode="values"):
        if "messages" in event:
            event["messages"][-1].pretty_print()


memory = MemorySaver()
graph = graph_builder.compile(
    checkpointer=memory, interrupt_before=["tools"])

config = {"configurable": {"thread_id": "2"}}

stream_graph_updates(
    graph,
    config,
    {"messages": [
        (
            "user",
            "I'm learning LangGraph. Could you do some research on it for me?"
        )
    ]})

# Update state
snapshot = graph.get_state(config)
print(snapshot)
# print(snapshot.next)

existing_message = snapshot.values["messages"][-1]
print(existing_message.tool_calls)

print("Original")
print("Message ID", existing_message.id)

# =========================================================
# Pattern1: Give an answer directly to chatbot node omitting tools.
# answer = (
#     "LangGraph is a library for building stateful, multi-actor applications with LLM."
# )
# new_messages = [
#     ToolMessage(
#         content=answer,
#         tool_call_id=existing_message.tool_calls[0]["id"]),
#     AIMessage(content=answer)
# ]

# new_messages[-1].pretty_print()
# graph.update_state(config, {"messages": new_messages})

# print("\n\nLast 2 messages;")
# print(graph.get_state(config).values["messages"][-2:])

# snapshot = graph.get_state(config)
# print(snapshot.values["messages"][-3:])
# print(snapshot.next)
# =========================================================

# =========================================================
# Pattern2: Overwrite exsiting message
new_tool_call = existing_message.tool_calls[0].copy()
new_tool_call["args"]["query"] = "LangGraph human-in-the-loop workflow"

new_message = AIMessage(
    content=existing_message.content,
    tool_calls=[new_tool_call],
    id=existing_message.id
)

print("Updated")
print(new_message.tool_calls[0])
print("Message ID", new_message.id)
graph.update_state(config, {"messages": [new_message]})

print("\n\nTool calls")
graph.get_state(config).values["messages"][-1].tool_calls
# =========================================================

# Resume the graph by streaming with an input of None and the existing config.
stream_graph_updates(graph, config, None)

# Confirm the effectivity of checkpoint usage
stream_graph_updates(
    graph,
    config,
    {"messages": [("user", "Remember what I'm learning about?")]})

from langgraph.checkpoint.memory import MemorySaver
from graph_builder import graph_builder


memory = MemorySaver()
graph = graph_builder.compile(
    checkpointer=memory, interrupt_before=["tools"])

config = {"configurable": {"thread_id": "2"}}
user_input = "I'm learning LangGraph. Could you do some research on it for me?"
# The config is the **second positional argument** to stream() or invoke()!
events = graph.stream(
    {"messages": [("user", user_input)]}, config, stream_mode="values"
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

# snapshot = graph.get_state(config)
# print(snapshot)
# print(snapshot.next)

# existing_message = snapshot.values["messages"][-1]
# print(existing_message.tool_calls)

# `None` will append nothing new to the current state,
# letting it resume as if it had never been interrupted
events = graph.stream(None, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

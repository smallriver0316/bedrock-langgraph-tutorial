from langgraph.checkpoint.memory import MemorySaver
from graph_builder_with_human_node import graph_builder

memory = MemorySaver()
graph = graph_builder.compile(
    checkpointer=memory,
    interrupt_before=["human"])
config = {"configurable": {"thread_id": "4"}}


def stream_graph_updates(user_input: str):
    for event in graph.stream(
        {"messages": [("user", user_input)]}, config, stream_mode="values"
    ):
        if "messages" in event:
            event["messages"][-1].pretty_print()


user_input = "I'm learning LangGraph. Could you do some research on it for me?"

stream_graph_updates(user_input)

user_input = "Ya that's helpful. Maybe I'll build an autonomous agent with it!"

stream_graph_updates(user_input)

to_replay = None

for state in graph.get_state_history(config):
    print(
        "Num of Messages: ",
        len(state.values["messages"]),
        ", Next: ",
        state.next)
    print("-" * 80)
    if len(state.values["messages"]) == 6:
        to_replay = state

print(to_replay.next)
print(to_replay.config)

for event in graph.stream(None, to_replay.config, stream_mode="values"):
    if "messages" in event:
        event["messages"][-1].pretty_print()

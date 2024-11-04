from langgraph.checkpoint.memory import MemorySaver
from graph_builder_with_human_node import graph_builder, create_response

memory = MemorySaver()
graph = graph_builder.compile(
    checkpointer=memory,
    interrupt_before=["human"])

config = {"configurable": {"thread_id": "3"}}

user_input = "I need some expert guidance for building this AI agent. Could you request assistance for me?"

for event in graph.stream(
    {"messages": [("user", user_input)]}, config, stream_mode="values"
):
    if "messages" in event:
        event["messages"][-1].pretty_print()

snapshot = graph.get_state(config)
print(snapshot.next)

ai_message = snapshot.values["messages"][-1]
human_response = (
    "We, the experts are here to help! We'd recommend you check out LangGraph to build your agent."
    " It's much more reliable and extensible than simple autonomous agents."
)
tool_message = create_response(human_response, ai_message)
graph.update_state(config, {"messages": [tool_message]})

print(graph.get_state(config).values["messages"])

for event in graph.stream(None, config, stream_mode="values"):
    if "messages" in event:
        event["messages"][-1].pretty_print()

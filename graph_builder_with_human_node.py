from typing import Annotated
from langchain_aws import ChatBedrockConverse
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import AIMessage, ToolMessage
from typing_extensions import TypedDict
from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in the case, it appends messages to the list,
    # rather than overwriting them)
    messages: Annotated[list, add_messages]
    ask_human: bool


class RequestAssistance(BaseModel):
    """Escalate the conversation to an expert.
    Use this if you are unable to assist directly
    or if the user requires support beyond your permissions.
    To use this function,
    relay the user's 'request' so the expert can provide the right guidance.
    """
    request: str


tool = TavilySearchResults(max_results=2)
tools = [tool]
tool_node = ToolNode(tools=[tool])

model = ChatBedrockConverse(
    model="anthropic.claude-3-haiku-20240307-v1:0"
    ).bind_tools(tools + [RequestAssistance])


def chatbot(state: State):
    response = model.invoke(state["messages"])
    ask_human = False
    if (response.tool_calls
            and response.tool_calls[0]["name"] == RequestAssistance.__name__):
        ask_human = True

    return {"messages": [response], "ask_human": ask_human}


def create_response(response: str, ai_message: AIMessage):
    return ToolMessage(
        content=response,
        tool_call_id=ai_message.tool_calls[0]["id"]
    )


def human_node(state: State):
    new_messages = []
    if not isinstance(state["messages"][-1], ToolMessage):
        # Typically, the user will have updated the state during interrupt.
        # If they chose not to, we will include a placeholder ToolMessage to
        # let the LLM continue.
        new_messages.append(
            create_response("No response from human.", state["messages"][-1])
        )
    return {
        "messages": new_messages,
        "ask_human": False
    }


def select_next_node(state: State):
    if state["ask_human"]:
        return "human"
    return tools_condition(state)


# Construct graph
graph_builder = StateGraph(State)

# Add nodes
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)
graph_builder.add_node("human", human_node)
# Add edges
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    select_next_node,
    {"human": "human", "tools": "tools", END: END}
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("human", "chatbot")
graph_builder.add_edge("chatbot", END)

import os
import lab_details
from langchain_core.messages import (
    BaseMessage,
    ToolMessage,
    HumanMessage,
)
from langchain_experimental.utilities import PythonREPL
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, StateGraph
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
import doctor_timeslot
from langgraph.checkpoint.sqlite import SqliteSaver
import operator
from typing import Annotated, Sequence, TypedDict
from langchain_groq import ChatGroq
from typing_extensions import TypedDict
import functools
from langchain_core.messages import AIMessage

memory = SqliteSaver.from_conn_string(":memory:")

os.environ["LANGCHAIN_API_KEY"] = ''
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Multi-agent Collaboration"

llm = ChatGroq(model="llama3-70b-8192",api_key='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')

doctor_calender = doctor_timeslot.get_doctor_calendar()


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    sender: str

system_prompt_slot_search_node = f"""
System: You are an appointment segregator and schedular. You have the following slot details with you {doctor_calender}.
According to the user or patient query and the data which you have, give the appropriate answer. Always return continue, because you are just
an  info provider never end the conversation, the other node will be responsible for having the conversation and to end it always, 
which means you will always return continue
"""

firstCallSlotSearchNode = True
def slot_search_node(state: AgentState):
    global firstCallSlotSearchNode
    if firstCallSlotSearchNode:
        state["messages"].append(system_prompt_slot_search_node)
        firstCallSlotSearchNode = False
    return {"messages": [llm.invoke(state["messages"])]}

system_prompt_chat_bot_node = """
System: You are Dr. Aryan's assistant. Dr. Aryan is a Dentist. Your job is to chat with the patients that seek the consultation of Dr. Aryan.
    You should take the following actions as and when required - 
    1. Call slot_search_node to book an appointment for the patient. The slot_search_node has the info about Dr's available and booked slots.
       Call slot_search_node when appointment-related queries are asked.
    2. Whenever you want to ask a question to the user or require human intervention, you should return __end__.
    3. Only you will be responsible to end the conversation.

    Please remember that the Doctor is very particular about timings. Never suggest the slots outside the slots of the doctor.

    You, as a supervisor chatbot, will be responsible for routing to different nodes and getting the user satisfied. To do that, follow the below instructions:
    - When you want to query appointment-related things, you should include __call_slot_search_node__ string in your response.
    - When you want to query lab tests-related things, you should include __call_lab_info_node__ string in your response.

    If the user's concern is related to severe pain, follow these steps:
    - Ask if the user has had an X-ray done in the last 3 days. If yes, proceed to schedule an appointment with Dr. Aryan.
    - If no, inform the user that it is mandatory to get an X-ray before the consultation. The X-ray facility is available within the hospital, 
      and it will help the doctor to observe and consult the patient well.
    - Prompt the user to ask about available slots for the X-ray.

    Always inform the user that the X-ray is a prerequisite for the consultation if they haven't had one in the last 3 days, 
    and ensure they understand they need to get this done before scheduling an appointment with the doctor.

    Don't forget to add a smiling emoji in the response if an appointment is successfully scheduled.

    A special care should be taken if the user or patient has already booked an appointment for consultation or for the X-ray. 
    Ensure that any new appointment does not overlap with previous choices or appointments. If the user or patient is trying to
    select overlapping timings, please warn them.
    
    We have a router function that directs the program to consider which node to call at runtime.
"""


firstCallChatBotNode = True
def chat_bot_node(state: AgentState):
    global firstCallChatBotNode
    if firstCallChatBotNode:
        state["messages"].append(system_prompt_chat_bot_node)
        firstCallChatBotNode = False
    return {"messages": [llm.invoke(state["messages"])]}

_lab_details_ = lab_details.get_X_ray_timetable()
system_prompt_lab_assistent_node = f"""
System: You are a lab assistent having info about the tests conducted in lab, you have the following details with you {_lab_details_}, you are a part of a graph,
and one of node in the graph, give the appropriate answer based on users question, only answer the question if it's related to the info you already have with
you,If you have the answer, return the answer else return __dont_know__
"""

firstCallLabAssistentNode = True
def lab_assistent_node(state: AgentState):
    global firstCallLabAssistentNode
    if firstCallLabAssistentNode:
        state["messages"].append(system_prompt_lab_assistent_node)
        firstCallLabAssistentNode = False
    return {"messages": [llm.invoke(state["messages"])]}


def router(state):
    messages = state["messages"]
    last_message = messages[-1]
    if "__dont_know__" in last_message.content:
        print('Irrelevent Question Asked')
        return "__end__"
    if "__call_slot_search_node__" in last_message.content:
        return "call_slot_search"
    if "__call_lab_info_node__" in last_message.content:
        return "call_lab_info"
    if "__end__" in last_message.content:
        return '__end__'
    return "__end__"

# Graph definition
workflow = StateGraph(AgentState)
workflow.add_node("slot_search", slot_search_node)
workflow.add_node("chat_bot", chat_bot_node)
workflow.add_node("lab_assistent", lab_assistent_node)

workflow.add_conditional_edges(
    "slot_search",
    router,
    {"continue": "chat_bot", "__end__": END},
)
workflow.add_conditional_edges(
    "chat_bot",
    router,
    {"call_slot_search": "slot_search", "call_lab_info": 'lab_assistent', '__end__': END},
)
workflow.add_conditional_edges(
    "lab_assistent",
    router,
    {"continue": "chat_bot", "__end__": END},
)

workflow.set_entry_point("chat_bot")

graph = workflow.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}


# Main loop for user interaction
# while True:
#     user_input = input("User: ")
#     if user_input.lower() in ["quit", "exit", "q"]:
#         print("Goodbye!")
#         break
#     events = graph.stream({"messages": [("user", user_input)]}, config=config, stream_mode="values")
#     for event in events:
#         for message in event["messages"]:
#             print(message)

while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break
    events = graph.stream({"messages": [("user", user_input)]},config=config,stream_mode="values")
    for event in events:
        event["messages"][-1].pretty_print()

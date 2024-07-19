from dotenv import load_dotenv
from datetime import datetime
from typing import List
import streamlit as st
import uuid
import json
import os

from langchain_core.tools import tool
# from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_huggingface import HuggingFacePipeline, HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage, ToolMessage

load_dotenv()

model = os.getenv('LLM_MODEL', 'HuggingFaceH4/zephyr-7b-beta')


def test_func(test_func_arg):
    """
    Prints out an argument passed to it

    Example call:

    test_func('today is a good day')
    Args:
        test_func_arg (str): text to print
    Returns:
        str: SOME BULLSHIt
    """

    print('******************received text is \n', test_func_arg, '\n***end of received text')
    try:
        return json.dumps({'a':''}, indent=2)
    except Exception as e:
        return f"Exception when calling TEST FUNC: {e}"
 

@st.cache_resource
def get_local_model():
    return HuggingFaceEndpoint(
        repo_id=model,
        task="text-generation",
        max_new_tokens=1024,
        do_sample=False
    )

    # return HuggingFacePipeline.from_model_id(
    #     model_id=model,
    #     task="text-generation",
    #     pipeline_kwargs={
    #         "max_new_tokens": 1024,
    #         "top_k": 50,
    #         "temperature": 0.4
    #     },
    # )

llm = get_local_model()     

available_tools = {
    "test_func": test_func
}

tool_descriptions = [f"{name}:\n{func.__doc__}\n\n" for name, func in available_tools.items()]

class ToolCall(BaseModel):
    name: str = Field(description="Name of the function to run")
    args: dict = Field(description="Arguments for the function call (empty if no arguments are needed for the tool call)")    

class ToolCallOrResponse(BaseModel):
    tool_calls: List[ToolCall] = Field(description="List of tool calls, empty array if you don't need to invoke a tool")
    content: str = Field(description="Response to the user if a tool doesn't need to be invoked")

tool_text = f"""
You always respond with a JSON object that has two required keys.

tool_calls: List[ToolCall] = Field(description="List of tool calls, empty array if you don't need to invoke a tool")
content: str = Field(description="Response to the user if a tool doesn't need to be invoked")

Here is the type for ToolCall (object with two keys):
    name: str = Field(description="Name of the function to run (NA if you don't need to invoke a tool)")
    args: dict = Field(description="Arguments for the function call (empty array if you don't need to invoke a tool or if no arguments are needed for the tool call)")

Don't start your answers with "Here is the JSON response", just give the JSON.

The tools you have access to are:

{"".join(tool_descriptions)}

Any message that starts with "Thought:" is you thinking to yourself. This isn't told to the user so you still need to communicate what you did with them.
Don't repeat an action. If a thought tells you that you already took an action for a user, don't do it again.
"""       

def prompt_ai(messages, nested_calls=0, invoked_tools=[]):
    if nested_calls > 3:
        raise Exception("Failsafe - AI is failing too much!")

    # First, prompt the AI with the latest user message
    parser = JsonOutputParser(pydantic_object=ToolCallOrResponse)
    chatbot = ChatHuggingFace(llm=llm) | parser
    
    try:
        ai_response = chatbot.invoke(messages)
    except Exception as e:
        st.error(f"Error invoking AI: {e}")
        return prompt_ai(messages, nested_calls + 1)

    print(f"AI Response: {ai_response}")

    # Second, see if the AI decided it needs to invoke a tool
    has_tool_calls = len(ai_response["tool_calls"]) > 0
    if has_tool_calls:
        # Next, for each tool the AI wanted to call, call it and add the tool result to the list of messages
        for tool_call in ai_response["tool_calls"]:
            if str(tool_call) not in invoked_tools:
                tool_name = tool_call["name"].lower()
                selected_tool = available_tools.get(tool_name)
                if selected_tool:
                    tool_output = selected_tool(**tool_call["args"])
                    messages.append(AIMessage(content=f"Thought: - I called {tool_name} with args {tool_call['args']} and got back: {tool_output}."))
                    invoked_tools.append(str(tool_call))
                else:
                    st.error(f"Tool {tool_name} not found.")
                    return {"content": f"Tool {tool_name} not found.", "tool_calls": []}
            else:
                return ai_response

        # Prompt the AI again now that the result of calling the tool(s) has been added to the chat history
        return prompt_ai(messages, nested_calls + 1, invoked_tools)

    return ai_response


def main():
    st.title("Chatbot")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content=f"You are a personal assistant who helps print to console some of thing that human asks you to print.")
        ]

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        message_json = json.loads(message.json())
        message_type = message_json["type"]
        message_content = message_json["content"]
        if message_type in ["human", "ai", "system"] and not message_content.startswith("Thought:"):
            with st.chat_message(message_type):
                st.markdown(message_content)        

    # React to user input
    if prompt := st.chat_input("What would you like to do today?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append(HumanMessage(content=prompt))

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            ai_response = prompt_ai(st.session_state.messages)
            st.markdown(ai_response['content'])
        
        st.session_state.messages.append(AIMessage(content=ai_response['content']))


if __name__ == "__main__":
    main()
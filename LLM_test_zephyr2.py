from dotenv import load_dotenv
import os

from huggingface_hub import login
from transformers import Tool, ReactCodeAgent, HfEngine


load_dotenv()

# login(os.getenv('HUGGINGFACEHUB_API_TOKEN'))

model = os.getenv('LLM_MODEL', 'HuggingFaceH4/zephyr-7b-beta')

llm_engine = HfEngine(model=model)


agent = ReactCodeAgent(tools=[], 
                  additional_authorized_imports=['search', 'ask_search_agent'], 
                  llm_engine=llm_engine, 
                  add_base_tools=True)
# print(agent.system_prompt_template)
try:
    agent.run("Hi, my name is Boris, who are you?")
except Exception as e:
    print('-----------------------------------------------------------------')
    print(e)
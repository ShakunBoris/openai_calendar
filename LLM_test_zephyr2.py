from dotenv import load_dotenv
import os

from huggingface_hub import login
from transformers import Tool, ReactCodeAgent, HfEngine, ReactJsonAgent
from transformers.agents import CodeAgent

load_dotenv()

# login(os.getenv('HUGGINGFACEHUB_API_TOKEN'))

# model = os.getenv('LLM_MODEL', 'HuggingFaceH4/zephyr-7b-beta')
model = os.getenv('Groq/Llama-3-Groq-8B-Tool-Use')

llm_engine = HfEngine(model=model)


agent = ReactJsonAgent(tools=[], 
                #   'search', 'ask_search_agent'
                #   additional_authorized_imports=[], 
                  llm_engine=llm_engine, 
                  add_base_tools=True)
# print(agent.system_prompt_template)
try:
    agent.run("Привет, ты кто? Просто напиши ответ как понимаешь, без использования дополнительных инструментов")
except Exception as e:
    print('-----------------------------------------------------------------')
    print(e)
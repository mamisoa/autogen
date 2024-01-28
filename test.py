import autogen
from autogen import config_list_from_json

from typing_extensions import Annotated

import holidays
from datetime import datetime, timedelta

OS_FLAG = True

oai_model_list = [
                "gpt-3.5-turbo",
                #   "gpt-3.5-turbo-16k",
                #   "gpt-3.5-turbo-1106",
                #   "gpt-4",
                #   "gpt-4-32k",
                #   "gpt-4-1106-preview",
                #   "gpt-4-vision-preview"
                ] 

os_model_list = [   
                    "ollama",
                    # "lmstudio",
                    # "mistral-instruct-8k",
                    # "neural-chat-8k",
                ]

config_list_os = config_list_from_json(
    env_or_file="OAI_CONFIG_LIST",
    filter_dict={
        "model": os_model_list
    }
)

config_list_oai = config_list_from_json(
    env_or_file="OAI_CONFIG_LIST",
    filter_dict={
        "model": oai_model_list
    }
)


# Configure the Agents
llm_config_os = {
    "config_list": config_list_os,
    "cache_seed": None,
    "timeout": 60,
    "temperature": 0
    }


# Configure the Agents
llm_config_oai = {
    "config_list": config_list_oai,
    "cache_seed": None,
    "timeout": 60,
    "temperature": 0
    }

if OS_FLAG == True:
    llm_config = llm_config_os
else:
    llm_config = llm_config_oai

print('list: ', llm_config['config_list'])

# Agent to input surgery date and process appointments
scheduler = autogen.AssistantAgent(
    name="Scheduler",
    system_message="A helpful medical scheduler. You can provide code that will be tested. Post operative dates are on day 1,7 and 30. They cannot be on a weekend or a bank holiday. Use the library 'holidays' with ```holidays.BE()``` to find bank holidays in Belgium. Use strict MARKDOWN to tag the code. Use date format dd-mm-yyyy. Proceed step by step. Reply TERMINATE ONLY when task is COMPLETED.",
    llm_config=llm_config
)

# User Proxy to interact with the system
user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"last_n_messages": 2, "work_dir": "test", "use_docker": False},
    # system_message="You are a proxy user. You only execute code and report errors to assistants so that they can correct it. Give a summary with the word 'TERMINATE' ONLY when the task is COMPLETED.",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    # llm_config=llm_config_oai,
)

user_proxy.initiate_chat(
    scheduler,
    message="Generate the postoperative dates if surgery is on 16/02/2024.",
)
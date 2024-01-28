import autogen
from autogen import config_list_from_json

from typing import Literal

from pydantic import BaseModel, Field
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
    "openhermes25",
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

if OS_FLAG == True:
    # Configure the Agents
    llm_config = {
        "config_list": config_list_os,
        "cache_seed": None,
        "timeout": 60,
        "temperature": 0
        }
    # llm_config['functions'] = [
    #     {
    #         "name": "calculate_appointments",
    #         "description": "caculates the postoperative appointments",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "surgery_date": {
    #                     "type": "string",
    #                     "description": "surgery date"
    #                 }
    #             },
    #             "required": ["surgery_date"],
    #         }
    #     }
    # ]
else:
    # Configure the Agents
    llm_config = {
        "config_list": config_list_oai,
        "cache_seed": None,
        "timeout": 60,
        "temperature": 0
        }
    


print('list: ', llm_config['config_list'])

# human_input_mode = "NEVER"
# human_input_mode = "TERMINATE"
human_input_mode = "ALWAYS"

# Agent to input surgery date and process appointments
scheduler = autogen.AssistantAgent(
    name="Scheduler",
    system_message="Calculates postoperative appointment dates, only use the function you have been provided with to generate the appropriate dates. All dates format are dd-mm-yyyy. Reply 'TERMINATE' ONLY when task is COMPLETED.",
    llm_config=llm_config
)

# User Proxy to interact with the system
user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"last_n_messages": 2, "work_dir": "surgery_scheduler",  "use_docker": False},
    system_message="You are a user proxy. You can only execute code to control validity of agents answers. Report errors to them. ONLY IF the task is COMPLETED, do a short summary finishing with the word 'TERMINATE'.",
    human_input_mode=human_input_mode,
    # default_auto_reply="Continue",
    max_consecutive_auto_reply=10,
    # llm_config=llm_config
)

# Define a function to adjust the appointment date
def adjust_date(date, country_holidays):
    initial_date = date
    while date.weekday() > 4 or date in country_holidays:
        date += timedelta(days=1)
        print(f"{initial_date} adjusted to: {date}")  # Debug print
    return date

# Define a function to calculate appointment dates
@user_proxy.register_for_execution()
@scheduler.register_for_llm(description="Calculates the postoperative dates.")
def calculate_appointments(
    surgery_date: Annotated[str, "Date of surgery"],
    country_holidays=holidays.BE()
    ) -> list:
    surgery_date = datetime.strptime(surgery_date, "%d-%m-%Y")
    dates = [surgery_date + timedelta(days=i) for i in [1, 7, 30]]
    adjusted_dates = [adjust_date(date, country_holidays) for date in dates]
    return [date.strftime("%d-%m-%Y") for date in adjusted_dates]

user_proxy.initiate_chat(
    scheduler,
    message="Give me the postoperative dates if surgery is on 16/02/2024",
)


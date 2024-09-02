import openai
from models.src import Activity, Flow
from typing import List
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
import services.prompts as p 
from models.utils import print_flows, print_entities
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

class NLPService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = self.api_key
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0, streaming=True, model_kwargs={"response_format": {"type": "json_object"}})
        
    def decide_flow(self, flows: List[Flow], activity: Activity, activity_history: List[Activity]):
        chat_history = []
        print(activity_history)
        for act in activity_history[:-1]:
            chat_history.append((act.sender, str(act.content)))
        trigger_flow_chain = p.trigger_flow_prompt | self.llm | JsonOutputParser()
        response = trigger_flow_chain.invoke({"input": activity.content, "flows": print_flows(flows), "chat_history": chat_history})
        print(response)
        print(flows)
        if response["execute_flow"] == True:
            for flow in flows:
                if flow.__class__.__name__ == response["flow"]:
                    return {"execute_flow": True, "flow": flow, "message": ""}
        return response

    def extract_entities(self, activity:Activity, entities: List[str], activity_history: List[Activity]):
        chat_history = []
        for act in activity_history[:-1]:
            chat_history.append((act.sender, str(act.content)))
        entity_chain = p.parse_entities | self.llm | JsonOutputParser()
        pretty_entities = print_entities(entities)
        response = entity_chain.invoke({"input": activity.content, "entities": pretty_entities, "chat_history": chat_history})
        return response

    def basic_handler(self,flow:Flow, current_step: str,  error:str, activity: Activity, activity_history: List[Activity]):
        chat_history = []
        for act in activity_history[:-1]:
            chat_history.append((act.sender, str(act.content)))
        basic_handler_chain = p.basic_handler_prompt | self.llm | JsonOutputParser()
        flow_info = f"{flow.__class__.__name__}: {flow.descripcion}"
        steps_info = "\n"
        for step_id, step in flow.steps.items():
            steps_info += f"Step Id: '{step_id}' \n Descripción: {step.descripcion}\n"
        response = basic_handler_chain.invoke({"flow_info": flow_info,"steps_info": steps_info,"current_step": current_step,"error": error, "input": activity.content, "chat_history": chat_history})
        return response



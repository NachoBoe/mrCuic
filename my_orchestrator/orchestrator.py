from pydantic import BaseModel
from typing import List, Dict, Union, Optional, Callable, Any
from services.api_service import bt_api  # Import the bt_api function
from models.src import Flow, Step, Activity
from services.nlp_service import NLPService

class Orchestrator:
    def __init__(self, flows: List[Flow], nlp_service: NLPService, websocket):
        self.flows = flows
        self.nlp_service = nlp_service
        self.websocket = websocket
        self.current_flow: Flow = None
        self.current_step: Step = None
        self.flow_memory = []
        self.state_memory = []
        self.suggested_default = ["Transferir dinero", "Consultar saldo", "Ayuda"]
        
    async def on_start(self):
        start_activity = Activity(
            type="message",
            content="Hola! Soy MrQuick, su asistente financiero. ¿En qué puedo ayudarte hoy?",
            sender="ai"
        )
        await self.send_activity(start_activity)
        await self.send_suggested_default()

    async def on_activity(self, activity: Activity):
        self.state_memory.append(activity)
        self.flow_memory.append(activity)
        if self.current_flow:
            if self.current_step.type == "parseActivity":
                await self.advance_flow(activity)
            else:
                pass
        else:
            decision = self.nlp_service.decide_flow(self.flows, activity,self.flow_memory)
            print(decision)
            if decision["execute_flow"]:
                self.current_flow = decision["flow"]
                self.current_step = self.current_flow.steps[self.current_flow.init_step]
                await self.advance_flow(activity)
            else:
                response_activity = Activity(
                    type="message",
                    content=decision["message"],
                    sender="ai"
                )
                await self.send_activity(response_activity)
                await self.send_suggested_default()

    async def advance_flow(self, activity: Activity):
        resultado_step = await self.current_step.run_step(activity, self)
        print(resultado_step)
        if resultado_step["action"] == "advance":
            if resultado_step["next_step"] == "END":
                await self.end_flow()
            else:
                self.current_step = self.current_flow.steps[resultado_step["next_step"]]
                if self.current_step.type != "parseActivity":
                    await self.advance_flow(activity)
        elif resultado_step["action"] == "callHandler":
            await self.callHandler(resultado_step["handler"],resultado_step["error"], activity)


    async def end_flow(self):
        self.current_flow = None
        self.current_step = None
        await self.send_suggested_default()
        self.flow_memory = []
        
        
    async def send_suggested_default(self):
        suggested_activity = Activity(
            type="suggestion",
            content=self.suggested_default,
            sender="ai"
        )
        await self.send_activity(suggested_activity)
    
    async def send_activity(self, activity: Activity):
        await self.websocket.send_json(activity.dict())
        self.state_memory.append(activity)
        self.flow_memory.append(activity)
        
    async def callHandler(self, handler, error, activity):
        resultado = self.nlp_service.basic_handler(self.current_flow, self.current_step.id, error, activity, self.flow_memory)
        if resultado["msg"]:
            response_activity = Activity(
                type="message",
                content=resultado["msg"],
                sender="ai"
            )
            await self.send_activity(response_activity)
        
        if resultado["action"] == "goto":
            next_step = resultado["next_step"]
            if next_step == "END":
                await self.end_flow()
            else:
                self.current_step = self.current_flow.steps[next_step]
                await self.advance_flow(activity)
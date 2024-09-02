from pydantic import BaseModel
from typing import List, Dict, Optional, Union, Callable, Any

class Activity(BaseModel):
    type: str
    content: Any
    sender: str

class Step:
    def __init__(self, function: Callable[[Activity], None], id:str, type: str, descripcion:str):
        self.function = function
        self.id = id
        self.type = type
        self.descripcion = descripcion
        
    async def run_step(self, activity: Activity, orchestrator):
        return await self.function(activity,orchestrator)

class Flow:
    def __init__(self, trigger_phrases: List[str], steps: Dict[str,Step], descripcion: str, init_step: str):
        self.trigger_phrases = trigger_phrases
        self.steps = steps
        self.descripcion = descripcion
        self.init_step = init_step

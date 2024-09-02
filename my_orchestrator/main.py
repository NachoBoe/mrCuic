import uvicorn
from fastapi import FastAPI, WebSocket
from orchestrator import Orchestrator
from services.nlp_service import NLPService
from models.src import Activity, Flow
import yaml
import os 
import importlib.util
import inspect
import traceback
from dotenv import load_dotenv


load_dotenv("./.env")

app = FastAPI()

flows = []


directory = "flows"
for filename in os.listdir(directory):
    if filename.endswith(".py"):
        filepath = os.path.join(directory, filename)        
        module_name = filename[:-3]
        
        # Cargar el módulo
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Recorrer todos los elementos del módulo
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Flow) and obj is not Flow:
                instancia_flujo = obj()
                flows.append(instancia_flujo)

print(flows)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    nlp_service = NLPService(api_key=os.getenv("OPENAI_API_KEY"))
    orchestrator = Orchestrator(flows, nlp_service=nlp_service, websocket=websocket)
    await orchestrator.on_start()
    
    while True:
        data = await websocket.receive_json()
        print(data)
        try:
            activity = Activity(**data)
        except Exception as e:
            error_activity = Activity(
                type="message",
                content="Invalid activity format. Please check your request.",
                sender="bot"
            )
            await websocket.send_json(error_activity.model_dump())
        try:    
            await orchestrator.on_activity(activity)
        except Exception as e:
            error_activity = Activity(
                type="message",
                content="An error occurred. Please try again.",
                sender="bot"
            )
            await websocket.send_json(error_activity.model_dump())
            traceback.print_exc()
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

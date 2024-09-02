import requests
import json
from pydantic import BaseModel
from typing import List, Optional, Callable

from models.src import Flow, Step, Activity
from models.utils import bt_api, find_closest_match

class DictToObj:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                value = DictToObj(value)
            setattr(self, key, value)
    
    def __getitem__(self, item):
        return getattr(self, item)

class ConsultaSaldo(Flow):
    def __init__(self):
        super().__init__(
            trigger_phrases=['quiero ver mis cuentas', 'consultar saldo', 'saldo', 'mis cuentas'],
            steps={
                "step_1": Step(self.step_1, "step_1", "CallAPI", "Obtiene las cuentas del usuario."),
                "step_2": Step(self.step_2, "step_2", "sendUser", "Envía el saldo de las cuentas del usuario."),
                },
            descripcion="Este flujo permite consultar el saldo de las cuentas del usuario.",
            init_step="step_1"
        )
        self.FLOW_MEMORY = dict()

    
    async def step_1(self, activity: Activity, orquestrator):
        
        # OBTENER ENTRADAS
        # LLAMAR API
        endpoint = "get_accounts"
        data = dict()
        data["Oper"] = 1
        data["Estado"] = 'C'
        data["Page"] = 1
        data["Moneda"] = [0]
        method_type = "post"
        response = bt_api(method_type, endpoint, data)
        response = DictToObj(response)
        # OBTENER SALIDAS
        self.FLOW_MEMORY["cuentas"] = response.data.Cuentas
        self.FLOW_MEMORY["nombre_cuentas"] = [x['Nombre'] for x in response.data.Cuentas]
        self.FLOW_MEMORY["saldo_cuentas"] = [x['Saldo'] for x in response.data.Cuentas]
        self.FLOW_MEMORY["moneda_cuentas"] = [x['Moneda'] for x in response.data.Cuentas]
        self.FLOW_MEMORY["numero_cuentas"] = [x['ProdShort'] for x in response.data.Cuentas]
        # PROXIMO PASO
        return {"action": "advance","next_step": "step_2"}
        
    async def step_2(self, activity: Activity, orquestrator):
        
        # OBTENER ENTRADAS
        cuentas = self.FLOW_MEMORY["cuentas"]
        nombre_cuentas = self.FLOW_MEMORY["nombre_cuentas"]
        saldo_cuentas = self.FLOW_MEMORY["saldo_cuentas"]
        moneda_cuentas = self.FLOW_MEMORY["moneda_cuentas"]
        numero_cuentas = self.FLOW_MEMORY["numero_cuentas"]
        # ENVIAR ACTIVIDAD A USUARIO
        content = '\n\n'.join([nom + '\n' + num + '\n' + mon + sald  for nom,num,mon,sald in zip(nombre_cuentas, numero_cuentas, moneda_cuentas, saldo_cuentas)])
        response = Activity(
            type="message",
            content=content,
            sender="ai",
        )
        await orquestrator.send_activity(response)
        # PROXIMO PASO
        return {"action": "advance","next_step": "END"}
        
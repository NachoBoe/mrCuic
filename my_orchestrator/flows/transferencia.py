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

class Transferencias(Flow):
    def __init__(self):
        super().__init__(
            trigger_phrases=['quiero hacer una transferencia', 'transferir'],
            steps={
                "step_1": Step(self.step_1, "step_1", "parseActivity", "Extrae del mensaje disparador del flujo si se encuentra implicito el monto, la moneda, la cuenta de origen, el tipo de destinatario o la cuenta de destino."),
                "step_2": Step(self.step_2, "step_2", "sendUser", "Pregunta al usuario si el destinatario de la transferencia es una cuenta propia, un beneficiario precargado o un nuevo beneficiario."),
                "step_3": Step(self.step_3, "step_3", "sendUser", "Envía al usuario las opciones de destinatario de la transferencia como botones de sugerencia."),
                "step_4": Step(self.step_4, "step_4", "parseActivity", "Extrae del mensaje del usuario el tipo de destinatario de la transferencia."),
                "step_5": Step(self.step_5, "step_5", "CallAPI", "Obtiene las cuentas del usuario."),
                "step_6": Step(self.step_6, "step_6", "sendUser", "Pregunta al usuario el monto, la moneda y la cuenta de origen y la cuenta de destino de la transferencia."),
                "step_7": Step(self.step_7, "step_7", "parseActivity", "Extrae del mensaje del usuario el monto, la moneda, la cuenta de origen y la cuenta de destino de la transferencia."),
                "step_8": Step(self.step_8, "step_8", "CallAPI", "Realiza la primera instancia de la transferencia."),
                "step_9": Step(self.step_9, "step_9", "sendUser", "Envía al usuario el código de confirmación de la transferencia."),
                "step_10": Step(self.step_10, "step_10", "parseActivity", "Extrae del mensaje del usuario el código de confirmación de la transferencia."),
                "step_11": Step(self.step_11, "step_11", "CallAPI", "Si el código es correcto, se realiza la segunda instancia de la transferencia."),
                "step_12": Step(self.step_12, "step_12", "sendUser", "Envía al usuario la confirmación de la transferencia."),
                "step_13": Step(self.step_13, "step_13", "sendUser", "Envía al usuario un mensaje de error en caso de que el código de confirmación sea incorrecto."),
                },
            descripcion="Este flujo permite realizar una transferencia.",
            init_step="step_1"
        )
        self.FLOW_MEMORY = dict()

    
    async def step_1(self, activity: Activity, orquestrator):
        
        # OBTENER ENTRADAS
        # PARSEAR ACTIVIDAD ENTRANTE
        if activity.type != "message":
            return {"action": "callHandler", "handler": "basic_handler", "error": f"Se esperaba una respuesta tipo message, pero se recibio una respuesta tipo {activity.type}"}
        entities_metadata = {"cuenta_destino": {"descripcion": "Nombre de la cuenta de destino de la transferencia", "required": "False", "tipo": "string"}, "cuenta_origen": {"descripcion": "Nombre de la cuenta de origen de la transferencia", "required": "False", "tipo": "string"}, "moneda": {"descripcion": "Moneda de la transferencia. Las opciones son pesos uruguayos (corresponde a 0) o dolares (corresponde a 22)", "required": "False", "tipo": "integer"}, "monto": {"descripcion": "Monto a transferir", "required": "False", "tipo": "float"}, "tipo_destinatario": {"descripcion": "Tipo de destinatario de la transferencia. Las opciones son: 0 (en caso de querer transferir a una cuenta propia), 1 (en caso de querer transferir a un beneficiario precargado) o 2 (en caso de querer transferir a un nuevo beneficiario)", "required": "False", "tipo": "integer"}}
        parsed_result = orquestrator.nlp_service.extract_entities(activity, entities_metadata, orquestrator.flow_memory)
        for entity in entities_metadata.keys():
            if entity not in parsed_result.keys():
                if entities_metadata[f"{entity}"]["required"] == "False":
                    parsed_result[f"{entity}"] = None
                else:
                    return {"action": "callHandler", "handler": "basic_handler", "error": f"El campo {entity} es requerido"}
        # OBTENER SALIDAS
        self.FLOW_MEMORY["monto"] = parsed_result["monto"]
        self.FLOW_MEMORY["moneda"] = parsed_result["moneda"]
        self.FLOW_MEMORY["cuenta_origen_nomb"] = parsed_result["cuenta_origen"]
        self.FLOW_MEMORY["tipo_destinatario"] = parsed_result["tipo_destinatario"]
        self.FLOW_MEMORY["cuenta_destino_nomb"] = parsed_result["cuenta_destino"]
        # PROXIMO PASO
        if not parsed_result["tipo_destinatario"] is None:
            return {"action": "advance","next_step": "step_5"}
        if parsed_result["tipo_destinatario"] is None:
            return {"action": "advance","next_step": "step_2"}
        
    async def step_2(self, activity: Activity, orquestrator):
        
        # OBTENER ENTRADAS
        # ENVIAR ACTIVIDAD A USUARIO
        content = 'Elije una de las siguientes opciones: \n - Mis Cuentas \n - Mis Beneficiarios \n - Nuevo Beneficiario'
        response = Activity(
            type="message",
            content=content,
            sender="ai",
        )
        await orquestrator.send_activity(response)
        # PROXIMO PASO
        return {"action": "advance","next_step": "step_3"}
        
    async def step_3(self, activity: Activity, orquestrator):
        
        # OBTENER ENTRADAS
        # ENVIAR ACTIVIDAD A USUARIO
        content = ['Mis Cuentas', 'Mis Beneficiarios', 'Nuevo Beneficiario']
        response = Activity(
            type="suggestion",
            content=content,
            sender="ai",
        )
        await orquestrator.send_activity(response)
        # PROXIMO PASO
        return {"action": "advance","next_step": "step_4"}
        
    async def step_4(self, activity: Activity, orquestrator):
        
        # OBTENER ENTRADAS
        # PARSEAR ACTIVIDAD ENTRANTE
        if activity.type != "message":
            return {"action": "callHandler", "handler": "basic_handler", "error": f"Se esperaba una respuesta tipo message, pero se recibio una respuesta tipo {activity.type}"}
        entities_metadata = {"tipo_destinatario": {"descripcion": "Tipo de destinatario de la transferencia. Las opciones son: 0 (en caso de querer transferir a una cuenta propia), 1 (en caso de querer transferir a un beneficiario precargado) o 2 (en caso de querer transferir a un nuevo beneficiario)", "required": "True", "tipo": "integer"}}
        parsed_result = orquestrator.nlp_service.extract_entities(activity, entities_metadata, orquestrator.flow_memory)
        for entity in entities_metadata.keys():
            if entity not in parsed_result.keys():
                if entities_metadata[f"{entity}"]["required"] == "False":
                    parsed_result[f"{entity}"] = None
                else:
                    return {"action": "callHandler", "handler": "basic_handler", "error": f"El campo {entity} es requerido"}
        # OBTENER SALIDAS
        self.FLOW_MEMORY["tipo_destinatario"] = parsed_result["tipo_destinatario"]
        # PROXIMO PASO
        return {"action": "advance","next_step": "step_5"}
        
    async def step_5(self, activity: Activity, orquestrator):
        
        # OBTENER ENTRADAS
        cuenta_origen_nomb = self.FLOW_MEMORY["cuenta_origen_nomb"]
        cuenta_destino_nomb = self.FLOW_MEMORY["cuenta_destino_nomb"]
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
        self.FLOW_MEMORY["default_origen"] = [x['Producto'] for x in response.data.Cuentas][find_closest_match(cuenta_origen_nomb, [x['Nombre'] for x in response.data.Cuentas])]
        self.FLOW_MEMORY["default_destino"] = [x['Producto'] for x in response.data.Cuentas][find_closest_match(cuenta_destino_nomb, [x['Nombre'] for x in response.data.Cuentas])]
        # PROXIMO PASO
        return {"action": "advance","next_step": "step_6"}
        
    async def step_6(self, activity: Activity, orquestrator):
        
        # OBTENER ENTRADAS
        monto = self.FLOW_MEMORY["monto"]
        moneda = self.FLOW_MEMORY["moneda"]
        cuentas = self.FLOW_MEMORY["cuentas"]
        default_origen = self.FLOW_MEMORY["default_origen"]
        default_destino = self.FLOW_MEMORY["default_destino"]
        # ENVIAR ACTIVIDAD A USUARIO
        with open("adaptative_cards/entradas_transferencia.yaml", 'r') as file:
            yaml_template = file.read()
        data = dict()
        data["cuentas_origen"] = [{'title':x['Nombre'] + ' ' + str(x['Saldo']) + str(x['Moneda']), 'value': x['Producto']} for x in cuentas]
        data["cuentas_destino"] = [{'title':x['Nombre'] + ' ' + str(x['Saldo']) + str(x['Moneda']), 'value': x['Producto']} for x in cuentas]
        data["default_monto"] = monto
        data["default_moneda"] = moneda
        data["default_origen"] = f"'{default_origen}'"
        data["default_destino"] = f"'{default_destino}'"
        formatted_yaml = yaml_template.format(**data)
        content = formatted_yaml
        response = Activity(
            type="adaptive_card",
            content=content,
            sender="ai",
        )
        await orquestrator.send_activity(response)
        # PROXIMO PASO
        return {"action": "advance","next_step": "step_7"}
        
    async def step_7(self, activity: Activity, orquestrator):
        
        # OBTENER ENTRADAS
        # PARSEAR ACTIVIDAD ENTRANTE
        if activity.type != "adaptive_card_answer":
            return {"action": "callHandler", "handler": "basic_handler", "error": f"Se esperaba una respuesta tipo adaptive_card_answer, pero se recibio una respuesta tipo {activity.type}"}
        entities_metadata = {"cuenta_destino": {"descripcion": "Nombre de la cuenta de destino de la transferencia", "required": "True", "tipo": "string"}, "cuenta_origen": {"descripcion": "Nombre de la cuenta de origen de la transferencia", "required": "True", "tipo": "string"}, "moneda": {"descripcion": "Moneda de la transferencia. Las opciones son pesos uruguayos (corresponde a 0) o dolares (corresponde a 22)", "required": "True", "tipo": "integer"}, "monto": {"descripcion": "Monto a transferir", "required": "True", "tipo": "float"}}
        parsed_result = json.loads(activity.content)
        for entity in entities_metadata.keys():
            if entity not in parsed_result.keys():
                if entities_metadata[f"{entity}"]["required"] == "False":
                    parsed_result[f"{entity}"] = None
                else:
                    return {"action": "callHandler", "handler": "basic_handler", "error": f"El campo {entity} es requerido"}
        # OBTENER SALIDAS
        self.FLOW_MEMORY["cuenta_origen"] = parsed_result["cuenta_origen"]
        self.FLOW_MEMORY["cuenta_destino"] = parsed_result["cuenta_destino"]
        self.FLOW_MEMORY["monto"] = parsed_result["monto"]
        self.FLOW_MEMORY["moneda"] = parsed_result["moneda"]
        # PROXIMO PASO
        return {"action": "advance","next_step": "step_8"}
        
    async def step_8(self, activity: Activity, orquestrator):
        
        # OBTENER ENTRADAS
        cuenta_origen = self.FLOW_MEMORY["cuenta_origen"]
        cuenta_destino = self.FLOW_MEMORY["cuenta_destino"]
        monto = self.FLOW_MEMORY["monto"]
        moneda = self.FLOW_MEMORY["moneda"]
        # LLAMAR API
        endpoint = "transfers_myaccounts_confirm"
        data = dict()
        data["CuentaOrigen"] = cuenta_origen
        data["CuentaDestino"] = cuenta_destino
        data["Monto"] = monto
        data["Moneda"] = moneda
        data["Concepto"] = 'Referencia'
        method_type = "post"
        response = bt_api(method_type, endpoint, data)
        response = DictToObj(response)
        # OBTENER SALIDAS
        self.FLOW_MEMORY["conf_code"] = response.data.Numerador
        # PROXIMO PASO
        return {"action": "advance","next_step": "step_9"}
        
    async def step_9(self, activity: Activity, orquestrator):
        
        # OBTENER ENTRADAS
        conf_code = self.FLOW_MEMORY["conf_code"]
        # ENVIAR ACTIVIDAD A USUARIO
        content = 'Para confirmar la transferencia, envie el siguiente código de 4 dígitos: ' + str(conf_code)
        response = Activity(
            type="message",
            content=content,
            sender="ai",
        )
        await orquestrator.send_activity(response)
        # PROXIMO PASO
        return {"action": "advance","next_step": "step_10"}
        
    async def step_10(self, activity: Activity, orquestrator):
        
        # OBTENER ENTRADAS
        conf_code = self.FLOW_MEMORY["conf_code"]
        # PARSEAR ACTIVIDAD ENTRANTE
        if activity.type != "message":
            return {"action": "callHandler", "handler": "basic_handler", "error": f"Se esperaba una respuesta tipo message, pero se recibio una respuesta tipo {activity.type}"}
        entities_metadata = {"conf_code_recieved": {"descripcion": "Codigo que debe enviar el usuario para confirmar la transferencia.", "required": "True", "tipo": "integer"}}
        parsed_result = orquestrator.nlp_service.extract_entities(activity, entities_metadata, orquestrator.flow_memory)
        for entity in entities_metadata.keys():
            if entity not in parsed_result.keys():
                if entities_metadata[f"{entity}"]["required"] == "False":
                    parsed_result[f"{entity}"] = None
                else:
                    return {"action": "callHandler", "handler": "basic_handler", "error": f"El campo {entity} es requerido"}
        # OBTENER SALIDAS
        self.FLOW_MEMORY["conf_code_recieved"] = parsed_result["conf_code_recieved"]
        # PROXIMO PASO
        if parsed_result["conf_code_recieved"] == conf_code:
            return {"action": "advance","next_step": "step_11"}
        if parsed_result["conf_code_recieved"] != conf_code:
            return {"action": "advance","next_step": "step_13"}
        
    async def step_11(self, activity: Activity, orquestrator):
        
        # OBTENER ENTRADAS
        conf_code = self.FLOW_MEMORY["conf_code"]
        # LLAMAR API
        endpoint = "transfers_myaccounts_reconfirm"
        data = dict()
        data["Numerador"] = conf_code
        method_type = "post"
        response = bt_api(method_type, endpoint, data)
        response = DictToObj(response)
        # OBTENER SALIDAS
        self.FLOW_MEMORY["confirmation_data"] = response
        # PROXIMO PASO
        if response.success == True:
            return {"action": "advance","next_step": "step_12"}
        if response.success == False:
            return {"action": "advance","next_step": "step_13"}
        
    async def step_12(self, activity: Activity, orquestrator):
        
        # OBTENER ENTRADAS
        confirmation_data = self.FLOW_MEMORY["confirmation_data"]
        # ENVIAR ACTIVIDAD A USUARIO
        content = 'Transferencia realizada con éxito. El Numero de Control es:' + str(confirmation_data.data.NroControl)
        response = Activity(
            type="message",
            content=content,
            sender="ai",
        )
        await orquestrator.send_activity(response)
        # PROXIMO PASO
        return {"action": "advance","next_step": "END"}
        
    async def step_13(self, activity: Activity, orquestrator):
        
        # OBTENER ENTRADAS
        # ENVIAR ACTIVIDAD A USUARIO
        content = 'Código incorrecto. La transferencia fue cancelada'
        response = Activity(
            type="message",
            content=content,
            sender="ai",
        )
        await orquestrator.send_activity(response)
        # PROXIMO PASO
        return {"action": "advance","next_step": "END"}
        
# Nombre del Proyecto
Mr Cuic

## Descripción

Implementación del backend y frontend the mrCuic

## Instalación

Para instalar las dependencias, es necesario tener conda (https://conda.io/projects/conda/en/latest/user-guide/install/windows.html) y node (https://nodejs.org/en/download/package-manager) instalados.

En una terminal, correr:

    conda create -n mrquick
    conda activate mrquick
    pip install -r my_orchestrator/requirements.txt

En una segunda terminal correr:

    cd frontend
    npm install

## Uso
Este proyecto utiliza el cliente de OpenAi. Para poder utilizarlo es necesario una API KEY. Agregar en la carpete my_orchestrator un archivo .env y agregar la api key como variable de entorno (OPENAI_API_KEY="my_api_key")

Para correr el proyecto, seguir estos pasos:

En una terminal, correr:

    conda activate mrquick
    cd my_orchestrator
    python main.py

En una segunda terminal correr:

    cd frontend
    npm run dev



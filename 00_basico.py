# Capa 0: El agente más básico
#
# Solo modelo + pregunta. Responde con conocimiento general
# no sabe nada de tarjetas chilenas ni tiene personalidad.
#
# Ejecutar: python 00_basico.py

import os
from strands.models.openai import OpenAIModel
from strands import Agent
from strands.models.anthropic import AnthropicModel
from dotenv import load_dotenv
load_dotenv()

if os.getenv("OPENAI_API_KEY"):
    modelo = OpenAIModel(
        model_id="gpt-4o-mini",
        params={"max_tokens": 1000},
    )
elif os.getenv("ANTHROPIC_API_KEY"):
    modelo = AnthropicModel(
        model_id="claude-3-5-haiku-20241022",
        max_tokens=1200,
    )
else:
    raise ValueError(
        "No se encontró ANTHROPIC_API_KEY ni OPENAI_API_KEY en el entorno.")

agente = Agent(model=modelo)

agente("¿Qué tarjeta de crédito me conviene si viajo mucho?")

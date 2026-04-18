# Capa 1: System prompt
#
# Mismo modelo, misma pregunta — pero ahora responde
# como asesor financiero especializado en tarjetas chilenas.
#
# Ejecutar: python 01_system_prompt.py

import os
from strands import Agent
from strands.models.anthropic import AnthropicModel
from strands.models.openai import OpenAIModel
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

agente = Agent(
    model=modelo,
    system_prompt="""Eres un asesor financiero experto en tarjetas de crédito chilenas.

Tu rol:
1. Recomendar tarjetas según el perfil y necesidades del usuario.
2. Explicar brevemente por qué recomiendas cada tarjeta.
3. Responder siempre en español.
4. Ser honesto: si una tarjeta no conviene para el perfil, decirlo.
5. Mantener las respuestas concisas — máximo 2-3 párrafos.""",
)

agente("¿Qué tarjeta de crédito me conviene si viajo mucho?")

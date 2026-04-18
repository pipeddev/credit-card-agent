# Capa 2: Tools — el asesor conoce tu dataset
#
# Agregamos @tool que busca en las tarjetas chilenas reales.
# El agente decide cuándo y cómo usar la herramienta.
#
# Ejecutar: python 02_tools.py

import json
from pathlib import Path
import os
from strands import Agent, tool
from strands.models.anthropic import AnthropicModel
from strands.models.openai import OpenAIModel

from dotenv import load_dotenv
load_dotenv()

TARJETAS = json.loads(Path("data/tarjetas.json").read_text(encoding="utf-8"))


@tool
def buscar_tarjetas(
    sin_anualidad: bool = False,
    con_millas: bool = False,
    con_cashback: bool = False,
    banco: str = "",
    renta_maxima: int = 0,
) -> str:
    """Busca tarjetas de crédito en el catálogo de tarjetas chilenas.
    Filtra por características específicas.
    Retorna nombre, banco, anualidad, cashback y beneficios.
    Usa esta herramienta siempre que el usuario pregunte por una tarjeta específica.

    Args:
        sin_anualidad: True si el usuario no quiere pagar anualidad.
        con_millas: True si quiere acumular millas (LATAM u otras).
        con_cashback: True si quiere cashback en efectivo.
        banco: Banco preferido (ej: 'BCI', 'Santander'). Vacío para no filtrar.
        renta_maxima: Renta líquida máxima en pesos. 0 para no filtrar.
    """
    resultados = TARJETAS.copy()

    if sin_anualidad:
        resultados = [t for t in resultados if t["anualidad"] == 0]
    if con_millas:
        resultados = [t for t in resultados if t["millas"]]
    if con_cashback:
        resultados = [t for t in resultados if t["cashback"] > 0]
    if banco:
        resultados = [t for t in resultados if banco.lower()
                      in t["banco"].lower()]
    if renta_maxima > 0:
        resultados = [
            t for t in resultados if t["renta_minima"] <= renta_maxima]

    if not resultados:
        return "No encontré tarjetas con esos criterios. Intenta con criterios menos restrictivos."

    return json.dumps(resultados[:5], ensure_ascii=False, indent=2)


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
2. Usar tus herramientas para buscar en el catálogo real de tarjetas.
3. Explicar brevemente por qué recomiendas cada tarjeta.
4. Responder siempre en español.""",
    tools=[buscar_tarjetas],
)

agente("¿Qué tarjeta me conviene si soy universitario y no quiero pagar anualidad?")

# Capa 3: Multi-tool — el asesor razona con varias herramientas
#
# El agente decide qué herramienta usar y en qué orden.
# Aquí se ve el "agentic loop" real de Strands.
#
# Ejecutar: python 03_multi_tool.py

import json
from pathlib import Path
import os
from strands import Agent, tool
from strands.models.anthropic import AnthropicModel
from strands.models.openai import OpenAIModel
from dotenv import load_dotenv
load_dotenv()

TARJETAS = json.loads(Path("data/tarjetas.json").read_text(encoding='utf-8'))


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

    Args:
        sin_anualidad: True si el usuario no quiere pagar anualidad.
        con_millas: True si quiere acumular millas.
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
        return "No encontré tarjetas con esos criterios."
    return json.dumps(resultados[:5], ensure_ascii=False, indent=2)


@tool
def calcular_cashback(
    gasto_mensual: int,
    nombre_tarjeta: str = "",
) -> str:
    """Calcula el cashback o beneficio anual estimado según el gasto mensual.
    Si se entrega nombre_tarjeta, calcula para esa tarjeta específica.
    Si no, compara todas las tarjetas con cashback.
    Los montos son en pesos chilenos (CLP).

    Args:
        gasto_mensual: Gasto mensual total estimado en pesos chilenos.
        nombre_tarjeta: Nombre de la tarjeta a evaluar. Vacío para comparar todas.
    """
    total_anual = gasto_mensual * 12

    if nombre_tarjeta:
        card = next(
            (t for t in TARJETAS if nombre_tarjeta.lower()
             in t["nombre"].lower()), None
        )
        if card:
            cb = total_anual * (card["cashback"] / 100)
            neta = cb - card["anualidad"]
            return (
                f"Con {card['nombre']} y ${gasto_mensual:,}/mes:\n"
                f"  Cashback anual: ${cb:,.0f}\n"
                f"  Anualidad: -${card['anualidad']:,}\n"
                f"  Ganancia neta: ${neta:,.0f}/año\n"
                + ("  ✅ ¡Conviene!" if neta >
                   0 else "  ⚠️ La anualidad supera el cashback.")
            )

    resultados = sorted(
        [(t["nombre"], total_anual * (t["cashback"] / 100), t["anualidad"],
          total_anual * (t["cashback"] / 100) - t["anualidad"])
         for t in TARJETAS if t["cashback"] > 0],
        key=lambda x: x[3], reverse=True
    )
    lines = [f"Ranking cashback con ${gasto_mensual:,}/mes:"]
    for nombre, cb, anual, neta in resultados:
        lines.append(
            f"  {nombre}: ${cb:,.0f} − ${anual:,} anualidad = ${neta:,.0f} neto/año")
    return "\n".join(lines)


@tool
def comparar_tarjetas(tarjeta_1: str, tarjeta_2: str) -> str:
    """Compara dos tarjetas de crédito chilenas lado a lado.

    Args:
        tarjeta_1: Nombre de la primera tarjeta.
        tarjeta_2: Nombre de la segunda tarjeta.
    """
    def find(name):
        nl = name.lower()
        return next((t for t in TARJETAS if nl in t["nombre"].lower()), None)

    t1, t2 = find(tarjeta_1), find(tarjeta_2)
    if not t1:
        return f"No encontré '{tarjeta_1}'."
    if not t2:
        return f"No encontré '{tarjeta_2}'."

    rows = [
        ("Banco", t1["banco"], t2["banco"]),
        ("Anualidad", t1["anualidad_descripcion"],
         t2["anualidad_descripcion"]),
        ("Cashback", f"{t1['cashback']}%", f"{t2['cashback']}%"),
        ("Millas", "✓" if t1["millas"] else "✗", "✓" if t2["millas"] else "✗"),
        ("Renta mínima", f"${t1['renta_minima']:,}",
         f"${t2['renta_minima']:,}"),
    ]
    header = f"{'Criterio':<18} | {t1['nombre']:<26} | {t2['nombre']:<26}"
    sep = "─" * len(header)
    lines = [header, sep] + \
        [f"{r[0]:<18} | {r[1]:<26} | {r[2]:<26}" for r in rows]
    return "\n".join(lines)


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
1. Usar tus herramientas para dar respuestas basadas en datos reales.
2. Cuando el usuario mencione un monto de gasto, usa calcular_cashback.
3. Cuando quiera comparar dos tarjetas, usa comparar_tarjetas.
4. Responder siempre en español.""",
    tools=[buscar_tarjetas, calcular_cashback, comparar_tarjetas],
)

# El agente usa múltiples tools en una sola respuesta
agente("Gasto $600.000 al mes. ¿Me conviene más la CMR Falabella o la Santander Superdigital?")

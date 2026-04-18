# Capa 4: Memoria — el asesor te recuerda
#
# Agrega FileSessionManager para que las conversaciones
# persistan entre ejecuciones del script.
#
# Ejecutar: python 04_memoria.py
# Ejecutar de nuevo y preguntar "¿Qué me recomendaste?" — el agente recuerda.

import json
from pathlib import Path
import os
from strands import Agent, tool
from strands.models.anthropic import AnthropicModel
from strands.models.openai import OpenAIModel
from strands.session.file_session_manager import FileSessionManager
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
def calcular_cashback(gasto_mensual: int, nombre_tarjeta: str = "") -> str:
    """Calcula el cashback o beneficio anual estimado según el gasto mensual.

    Args:
        gasto_mensual: Gasto mensual total estimado en pesos chilenos.
        nombre_tarjeta: Nombre de la tarjeta a evaluar. Vacío para comparar todas.
    """
    total_anual = gasto_mensual * 12
    if nombre_tarjeta:
        card = next((t for t in TARJETAS if nombre_tarjeta.lower()
                    in t["nombre"].lower()), None)
        if card:
            cb = total_anual * (card["cashback"] / 100)
            neta = cb - card["anualidad"]
            return (
                f"Con {card['nombre']} y ${gasto_mensual:,}/mes:\n"
                f"  Cashback: ${cb:,.0f} − Anualidad: ${card['anualidad']:,} = ${neta:,.0f} neto/año\n"
                + ("  ✅ ¡Conviene!" if neta >
                   0 else "  ⚠️ La anualidad supera el cashback.")
            )
    resultados = sorted(
        [(t["nombre"], total_anual*(t["cashback"]/100), t["anualidad"],
          total_anual*(t["cashback"]/100)-t["anualidad"])
         for t in TARJETAS if t["cashback"] > 0],
        key=lambda x: x[3], reverse=True
    )
    lines = [f"Ranking cashback con ${gasto_mensual:,}/mes:"]
    for nombre, cb, anual, neta in resultados:
        lines.append(
            f"  {nombre}: ${cb:,.0f} − ${anual:,} = ${neta:,.0f} neto/año")
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
    return "\n".join([header, sep] + [f"{r[0]:<18} | {r[1]:<26} | {r[2]:<26}" for r in rows])


# ── Callback para mostrar el razonamiento del agente ──────────────────────────
_callback_state = {"after_tool": False}


def callback_handler(**kwargs):
    """Maneja callbacks del agente para mostrar razonamiento y uso de herramientas.

    Args:
        **kwargs: Diccionario con datos del callback, puede incluir 'data' y 'current_tool_use'.
    """
    if "data" in kwargs:
        if _callback_state["after_tool"]:
            print("\n💳 Asesor: ", end="", flush=True)
            _callback_state["after_tool"] = False
        print(kwargs["data"], end="", flush=True)
    if "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
        print(
            f"\n🔧 Usando tool: {kwargs['current_tool_use']['name']}...", flush=True)
        _callback_state["after_tool"] = True


# ── Session Management (+1 ticket) ────────────────────────────────────────────
Path("sessions").mkdir(exist_ok=True)

session_manager = FileSessionManager(
    session_id="asesor-tarjetas-chile",
    storage_dir="./sessions",
)

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
    agent_id="asesor-tarjetas",
    session_manager=session_manager,
    system_prompt="""Eres un asesor financiero experto en tarjetas de crédito chilenas.
Tienes memoria de conversaciones anteriores — úsala para personalizar tus respuestas.

Tu rol:
1. Usar tus herramientas para dar respuestas basadas en datos reales.
2. Cuando el usuario mencione gasto mensual, usa calcular_cashback.
3. Cuando quiera comparar tarjetas, usa comparar_tarjetas.
4. Recordar preferencias del usuario de sesiones anteriores.
5. Responder siempre en español.""",
    tools=[buscar_tarjetas, calcular_cashback, comparar_tarjetas],
    callback_handler=callback_handler,
)

# ── Loop conversacional ───────────────────────────────────────────────────────
print("💳 Asesor de Tarjetas de Crédito Chile")
print("   (escribe 'salir' para terminar)\n")

while True:
    pregunta = input("Tú: ").strip()
    if not pregunta or pregunta.lower() in ("salir", "exit", "q"):
        print("¡Hasta luego! Tu sesión fue guardada.")
        break
    print()
    agente(pregunta)
    print("\n")

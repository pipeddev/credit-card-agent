"""
💳 MCP Server — Credit Card Tools
Servidor MCP local que expone herramientas de tarjetas como protocolo estándar.
Correr con: python mcp_server.py
"""

import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("credit-cards-chile", stateless_http=True,
              host="0.0.0.0", port=8001)

# Cargar dataset
CARDS_PATH = Path(__file__).parent / "data" / "tarjetas.json"
with open(CARDS_PATH, encoding="utf-8") as f:
    CARDS_DB: list[dict] = json.load(f)


@mcp.tool()
def mcp_get_exchange_rate() -> str:
    """
    Retorna la tasa de cambio USD/CLP aproximada del día.
    Útil para que el agente contextualice anualidades en dólares.
    """
    # Simulado (en producción conectaría a una API real)
    usd_clp = 940
    return (
        f"Tasa de cambio aproximada: 1 USD = ${usd_clp:,} CLP\n"
        f"Ejemplo: Una anualidad de $120.000 CLP ≈ USD {120000/usd_clp:.0f}\n"
        f"Fuente: Valor referencial (simulado para demo)"
    )


@mcp.tool()
def mcp_get_bank_info(banco: str) -> str:
    """
    Retorna información general sobre un banco chileno:
    historia, calificación, cobertura de cajeros, atención al cliente.
    Bancos disponibles: BCI, Santander, BICE, Falabella, Ripley, Itaú, BancoEstado, Scotiabank
    """
    info = {
        "bci": {
            "nombre": "BCI (Banco de Crédito e Inversiones)",
            "tipo": "Banco privado chileno",
            "cajeros": "Más de 2.000 ATMs en Chile",
            "app": "BCI App — bien valorada en App Store",
            "fortaleza": "Amplia red en Chile continental y oficinas en el extranjero",
            "nota": "Muy buena relación con clientes PyME y personas naturales",
        },
        "santander": {
            "nombre": "Santander Chile",
            "tipo": "Filial del grupo español Santander",
            "cajeros": "Red Santander + convenio con Multicaja",
            "app": "App Santander — una de las mejor calificadas del mercado",
            "fortaleza": "Productos premium y beneficios para viajeros frecuentes",
            "nota": "Fuerte en segmento ABC1 y clientes con altos ingresos",
        },
        "bice": {
            "nombre": "BICE (Banco Internacional de Chile)",
            "tipo": "Banco privado chileno — grupo Matte",
            "cajeros": "Red propia + Redbanc",
            "app": "App BICE — funcional pero menos features que la competencia",
            "fortaleza": "Excelente servicio personalizado, foco en alto patrimonio",
            "nota": "Ideal para clientes premium que valoran atención exclusiva",
        },
        "falabella": {
            "nombre": "Banco Falabella",
            "tipo": "Banco del grupo Falabella (retail)",
            "cajeros": "ATMs en tiendas Falabella + Redbanc",
            "app": "App CMR — integrada con beneficios del grupo",
            "fortaleza": "La tarjeta más usada en Chile, integración total con el ecosistema Falabella",
            "nota": "Mejor si compras frecuentemente en Falabella, Tottus o Sodimac",
        },
        "bancoestado": {
            "nombre": "BancoEstado",
            "tipo": "Banco estatal de Chile",
            "cajeros": "La red más grande de Chile — más de 3.000 cajeros ServiEstado",
            "app": "App BancoEstado — ampliamente usada, mejoras constantes",
            "fortaleza": "Cobertura nacional incluyendo zonas rurales, accesible para todos",
            "nota": "La opción más inclusiva — sin renta mínima con CuentaRUT",
        },
        "scotiabank": {
            "nombre": "Scotiabank Chile",
            "tipo": "Filial del grupo canadiense Scotiabank",
            "cajeros": "Red propia + Redbanc",
            "app": "App Scotiabank — funcional",
            "fortaleza": "Buena oferta de tarjetas con millas LATAM",
            "nota": "Relevante si viajas seguido a Latinoamérica",
        },
        "itau": {
            "nombre": "Itaú Chile",
            "tipo": "Filial del grupo brasileño Itaú Unibanco",
            "cajeros": "Red propia + Redbanc",
            "app": "App Itaú — muy bien calificada, UX moderna",
            "fortaleza": "Cashback flexible: elige entre efectivo o millas",
            "nota": "Buena opción para quienes quieren flexibilidad en beneficios",
        },
        "ripley": {
            "nombre": "Banco Ripley",
            "tipo": "Banco del grupo Ripley (retail)",
            "cajeros": "ATMs en tiendas Ripley + Redbanc",
            "app": "App Ripley — integrada con tienda",
            "fortaleza": "Descuentos directos en tienda Ripley",
            "nota": "Conveniente solo si eres cliente frecuente de Ripley",
        },
    }

    banco_key = banco.lower().replace("banco", "").strip()
    for key, data in info.items():
        if key in banco_key or banco_key in key:
            return "\n".join([f"🏦 **{data['nombre']}**"] + [
                f"  {k.capitalize()}: {v}" for k, v in data.items() if k != "nombre"
            ])

    bancos_disponibles = ", ".join(info.keys())
    return f"No encontré info del banco '{banco}'. Bancos disponibles: {bancos_disponibles}"


@mcp.tool()
def mcp_get_market_tips() -> str:
    """
    Retorna tips actuales del mercado de tarjetas de crédito en Chile:
    tendencias, qué está de moda, qué beneficios son más valorados.
    """
    return """📊 Tips del mercado de tarjetas de crédito en Chile (2024-2025):

🔥 Tendencias actuales:
  • Las tarjetas con cashback están ganando popularidad vs millas
  • Tarjetas 100% digitales (sin sucursal) crecen fuerte: Superdigital, MACH
  • BNPL (Buy Now Pay Later) compite con tarjetas tradicionales en jóvenes
  • La gente prefiere tarjetas sin anualidad o con anualidad bonificable

💡 Qué buscan los chilenos hoy:
  1. Sin anualidad o anualidad muy baja
  2. Cuotas sin interés en el mayor número de comercios
  3. Cashback > millas (las millas son más difíciles de usar)
  4. App buena y pago por NFC/contactless
  5. Beneficios en delivery y streaming (Netflix, Uber Eats, etc.)

⚠️ Lo que debes evitar:
  • Tarjetas con tasa de interés muy alta (sobre 3% mensual)
  • Anualidades altas si tu gasto mensual es bajo
  • Tarjetas de retail si no compras en esa tienda
  • Pagar el mínimo — siempre paga el total del estado de cuenta

✅ Regla de oro:
  Si gastas menos de $300.000/mes → elige sin anualidad
  Si gastas más de $500.000/mes → evalúa cashback o millas
  Si viajas más de 4 veces al año → considera tarjeta con millas + sala VIP"""


if __name__ == "__main__":
    print("🚀 MCP Server 'credit-cards-chile' corriendo en http://localhost:8001")
    print("   Tools disponibles: mcp_get_exchange_rate, mcp_get_bank_info, mcp_get_market_tips")
    mcp.run(transport="streamable-http")

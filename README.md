# 💳 Asesor de Tarjetas de Crédito Chile

Agente conversacional que ayuda a encontrar la mejor tarjeta de crédito chilena según tu perfil y necesidades. Construido con **Strands Agents SDK** de AWS, compatible con **OpenAI** y **Anthropic Claude**, agregando capacidades paso a paso.

> 🎤 Presentado en **Nerdearla Chile 2026** — Workshop "Construye Agentes de IA con Open Source"

---

## ¿Qué hace?

Le describes tu situación en lenguaje natural y el agente razona, busca en el catálogo y te recomienda:

```
Tú: "Soy universitario, no quiero pagar anualidad"
💳 Asesor: Te recomiendo la BancoEstado Zero y la Santander Superdigital...

Tú: "Gasto $500.000 al mes, ¿cuál me da más cashback?"
🔧 Usando tool: calcular_cashback...
💳 Asesor: Con la Itaú Visa Signature ganarías $4.500 netos al año...

Tú: "¿Cuánto es esa anualidad en dólares?"
🔧 Usando tool: mcp_get_exchange_rate...
💳 Asesor: A la tasa actual de $940 CLP por dólar, serían USD 95...
```

---

## Requisitos

- Python 3.10+
- OpenAI API Key **o** Anthropic API Key

## Setup

```bash
# 1. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate       # Mac/Linux
.venv\Scripts\activate          # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear archivo .env con tu API key
echo "OPENAI_API_KEY=sk-..." > .env
# o
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

## Selección automática de modelo

El agente detecta automáticamente qué API key tienes disponible y usa el modelo correspondiente. No necesitas cambiar nada en el código:

```python
if os.getenv("OPENAI_API_KEY"):
    modelo = OpenAIModel(model_id="gpt-4o-mini", params={"max_tokens": 1000})
elif os.getenv("ANTHROPIC_API_KEY"):
    modelo = AnthropicModel(model_id="claude-3-5-haiku-20241022", max_tokens=1200)
else:
    raise ValueError("No se encontró ANTHROPIC_API_KEY ni OPENAI_API_KEY en el entorno.")
```

Esto demuestra una ventaja clave de Strands: es **model-agnostic**. Cambiar de provider es una sola línea de código.

---

## Archivos del proyecto

### `00_basico.py` — El agente más básico

El punto de partida. Solo modelo + pregunta. Responde con conocimiento general — no sabe nada de tarjetas chilenas específicas ni tiene personalidad definida.

```bash
python 00_basico.py
```

**Concepto:** `Agent` = modelo + loop. Sin más.

---

### `01_system_prompt.py` — Personalidad con system prompt

Mismo modelo, misma pregunta — pero ahora el agente responde como asesor financiero chileno. El system prompt define quién es y cómo debe comportarse.

```bash
python 01_system_prompt.py
```

**Concepto:** El system prompt transforma un modelo genérico en un experto con personalidad.

---

### `02_tools.py` — El agente busca en datos reales (`@tool`)

Agregamos el decorator `@tool` para que el agente busque en el catálogo real de 10 tarjetas chilenas. El agente decide cuándo y cómo usar la herramienta — no está hardcodeado.

```bash
python 02_tools.py
```

**Concepto:** `@tool` convierte una función Python en una herramienta que el agente puede invocar autónomamente. Este es el feature que otorga el primer ticket extra.

---

### `03_multi_tool.py` — Razonamiento con múltiples herramientas

El agente tiene 3 tools disponibles: `buscar_tarjetas`, `calcular_cashback` y `comparar_tarjetas`. Decide cuál usar (y en qué orden) según lo que el usuario pregunta — sin lógica hardcodeada.

```bash
python 03_multi_tool.py
```

**Concepto:** El "agentic loop" de Strands — el modelo razona, elige tools, ejecuta, y vuelve a razonar con los resultados.

---

### `04_memoria.py` — El asesor te recuerda (`FileSessionManager`)

Agrega `FileSessionManager` para que la conversación persista entre ejecuciones. Cierra el script, vuélvelo a abrir y el agente recuerda lo que hablaron antes.

```bash
python 04_memoria.py
# Cierra con Ctrl+C
python 04_memoria.py  # El agente recuerda la sesión anterior
```

**Concepto:** Session management — el estado de la conversación se guarda en `./sessions/` automáticamente. Este es el feature que otorga el segundo ticket extra.

---

### `05_mcp.py` — Herramientas externas via MCP

Conecta a un servidor MCP propio (`mcp_server.py`) que expone 3 tools adicionales via HTTP: tasa de cambio USD/CLP, información de bancos chilenos, y tendencias del mercado. El agente combina tools locales + tools MCP en una sola respuesta.

```bash
# Terminal 1 — levantar el servidor MCP
python mcp_server.py

# Terminal 2 — correr el agente
python 05_mcp.py
```

**Concepto:** MCP (Model Context Protocol) es un estándar abierto para exponer herramientas a agentes de IA. Permite separar el agente de sus fuentes de datos. Este es el feature que otorga el tercer ticket extra.

---

### `mcp_server.py` — Servidor MCP propio

Servidor HTTP construido con `fastmcp` que expone 3 herramientas:

- `mcp_get_exchange_rate` — tasa de cambio USD/CLP del día
- `mcp_get_bank_info` — información sobre un banco chileno específico
- `mcp_get_market_tips` — tendencias actuales del mercado de tarjetas

Corre en `http://localhost:8001`. El agente se conecta a él automáticamente al usar `05_mcp.py`.

---

### `data/tarjetas.json` — Dataset de tarjetas chilenas

10 tarjetas de crédito chilenas reales con datos estructurados: anualidad, cashback, millas, renta mínima, beneficios, perfil ideal. Fuente para todos los tools de búsqueda.

**Tarjetas incluidas:** BancoEstado Zero, Santander Superdigital, CMR Falabella, Ripley Mastercard, BCI Visa Classic, BCI Nova Gold, Scotiabank Visa Gold, Itaú Visa Signature, BICE Mastercard Black, Santander Visa Infinite.

---

**Demo recomendada para el booth:**

1. Mostrar `04_memoria.py` — cerrar y reabrir para demostrar memoria
2. Preguntar algo con gasto mensual — mostrar multi-tool reasoning
3. Preguntar por tasa en dólares con `05_mcp.py` — mostrar MCP en acción

---

## Stack

- [Strands Agents SDK](https://github.com/strands-agents/sdk-python) — AWS
- [OpenAI GPT-4o-mini](https://platform.openai.com/) o [Anthropic Claude Haiku](https://anthropic.com) — modelo de lenguaje (auto-detectado)
- [fastmcp](https://github.com/jlowin/fastmcp) — servidor MCP
- Python 3.10+

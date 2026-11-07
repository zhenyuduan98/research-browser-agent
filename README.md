# Research Browser Agent

[中文说明](README_zh.md)

A browser agent that helps a user finish web research which otherwise means opening sites, filling forms, and reading the results by hand.

Two cases are included:

- **Case 1. Competitive analysis.** Open competitor sites and turn positioning, features, and pricing into a comparison.
- **Case 2. Ctrip flight search.** Operate the Ctrip flight page and look up flights, for example a Christmas trip to Sydney.

The agent runtime is built on [OpenManus](https://github.com/FoundationAgents/OpenManus) (MIT). The work in this repository is the research workflow on top of that runtime: a web console, a travel knowledge file, a vision fallback for pages whose DOM is hard to read, and the two cases above.

## Architecture

```text
User
  |  CLI: python main.py
  |  Web: python app.py  ->  http://localhost:5172
  v
Manus agent
  plan -> tool call -> observe -> next step
  |
  +-- LLM (OpenAI-compatible chat API, tool calling)
  +-- web_search
  +-- browser_use
  |     Playwright drives a real Chromium window
  |     GUI-Plus vision fallback: screenshot -> click / type
  +-- knowledge/*.txt injected into the system prompt
  +-- optional Daytona sandbox for isolated code execution
```

| Piece | Role |
| --- | --- |
| `OpenManus-cy` | Agent loop, tools, and the Daytona sandbox |
| `OpenManus-gui` | FastAPI console used to watch a task step by step |
| `OpenManus-rag` | Loads `knowledge/*.txt` into the system prompt before the first step |
| `CASE-gui-plus使用` | Small script that asks a vision model for one GUI action |
| `CASE-daytona使用` | Small script that runs code inside a Daytona sandbox |

The model never receives a flight price or a competitor claim unless a tool returned it. The system prompt tells the agent not to invent live data.

## Case 1: competitive analysis

Ask the agent to compare products in one category. It searches for the official pages, opens each site, and extracts positioning, feature list, and public pricing into one write-up.

Example prompt:

```text
Compare Notion, Coda, and Outline on positioning, core features, and public pricing. Cite the page you read for each point.
```

What the run shows:

1. The planner splits the job into one site at a time.
2. `web_search` finds the official pages.
3. `browser_use` opens each page. If the DOM has no usable elements, GUI-Plus looks at a screenshot and returns a click or a type action.
4. The final message is a comparison grounded in those pages, not a generic product summary.

## Case 2: Ctrip flight search

Ask the agent to look up flights on Ctrip. A tested prompt is:

```text
搜索圣诞节飞悉尼的携程机票
```

What the run shows:

1. The agent opens `https://flights.ctrip.com/`.
2. It fills the departure city and the arrival city. On this page the input boxes are often missing from the DOM snapshot, so the vision model clicks the city field and types the city name.
3. `OpenManus-rag/knowledge/travel_tools.txt` also gives a direct Ctrip list URL (`oneway-{from}-{to}?depdate=YYYY-MM-DD`) so the agent can skip the calendar widget when a city code and a date are already known.

The browser window stays visible (`headless = false`) so the steps can be watched.

## Run

Python 3.12. Install dependencies once:

```bash
pip install -r OpenManus-gui/requirements.txt
python -m playwright install chromium
```

Set keys in the environment. Do not put them in a committed file.

```bash
# PowerShell
$env:DASHSCOPE_API_KEY = "your-dashscope-key"
$env:DAYTONA_API_KEY = "your-daytona-key"   # only for the sandbox case
```

Web console:

```bash
cd OpenManus-gui
python app.py
```

Open http://localhost:5172 and type a case prompt. `OpenManus-rag` is the same agent with the knowledge file loaded:

```bash
cd OpenManus-rag
python main.py
```

Vision-only check:

```bash
cd CASE-gui-plus使用
python 1-gui-plus使用.py
```

Sandbox check, after copying `CASE-daytona使用/.env.example` to `.env`:

```bash
cd CASE-daytona使用
python 1-daytona.py
```

## Configuration

`config/config.toml` is gitignored. Copy `config/config.example.toml` to `config/config.toml` and leave `api_key` empty, or fill it only on your machine. An empty `api_key` makes the process read `DASHSCOPE_API_KEY`. The default chat model is `qwen-max`, and the vision model is `qwen-vl-plus`, both through DashScope's OpenAI-compatible endpoint. `CASE-daytona使用/.env` is also gitignored; start from `.env.example`.

## Acknowledgements

Agent loop, tool protocol, and browser tool structure come from [OpenManus](https://github.com/FoundationAgents/OpenManus) by the MetaGPT / FoundationAgents community, released under the MIT License. See `OpenManus-cy/LICENSE`.

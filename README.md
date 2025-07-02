# LangSmith Log Analyzer

LangSmith Log Analyzer is an AI-powered system designed to analyze server logs using large language models (LLMs). It classifies log events, detects critical incidents, and generates structured reports and visual charts. The entire analysis process is accessible through a Streamlit-based interactive interface.


---

## Features

* Modular agent-based architecture
* LLM-powered log interpretation with LangChain + Ollama
* LangSmith integration for trace tracking and observability
* Automatic report generation in JSON and CSV formats
* Chart visualization with matplotlib
* Streamlit dashboard with file upload and real-time feedback
* Downloadable analysis reports (JSON, CSV)

---

## Project Structure

```
.
├── main.py                    # Command-line log processor
├── app.py  # Streamlit frontend interface
├── logs/
│   └── logs.txt               # Uploaded log file
├── results/
│   ├── report.json
│   ├── report.csv
│   └── charts/
│       ├── event_type_distribution.png
│       └── critical_vs_normal.png
├── agents/                    # Agent classes managing separate responsibilities
│   ├── collector.py           # Collects logs from source
│   ├── llm_agent.py           # Sends logs to LLM and parses output
│   ├── parser.py              # Optional data formatting or enrichment
│   ├── filter.py              # Identifies critical events
│   ├── alert.py               # Emits alerts for critical events
│   └── report.py              # Builds structured reports and visualizations
└── .env                       # Environment variables (LangSmith settings)
```

---

## Setup

### 1. Python Version

Requires Python 3.10 or higher.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables (`.env`)

Create a `.env` file in the root directory with the following content:

```
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=log-analyzer
LANGCHAIN_TRACING_V2=false
```

LangSmith API keys can be obtained at [https://smith.langchain.com](https://smith.langchain.com)

---

## Usage

### 1. Run from CLI

```bash
python main.py
```

### 2. Launch Streamlit App

```bash
streamlit run app.py
```

Within the UI:

* Upload a `.txt` log file
* View classification results and charts
* Download structured reports

---

## Technologies Used

* LangChain
* LangSmith
* Ollama
* Streamlit
* Matplotlib

---


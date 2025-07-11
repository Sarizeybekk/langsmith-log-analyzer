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
![image](https://github.com/user-attachments/assets/5c7fd20b-8c56-454d-b4b5-00087f204f80)
<img width="1095" alt="Ekran Resmi 2025-07-02 03 09 05" src="https://github.com/user-attachments/assets/83280a2c-6136-4a2f-a086-aeff7223f258" />

Versiyon-2: Güncel hali:
<img width="1500" height="827" alt="Ekran Resmi 2025-07-11 19 43 32" src="https://github.com/user-attachments/assets/64673a31-6227-4962-a264-8517b02eb995" />
<img width="1491" height="797" alt="Ekran Resmi 2025-07-11 19 43 46" src="https://github.com/user-attachments/assets/43a8737d-d45c-4aca-b8f9-394b2e1720e0" />

<img width="1486" height="747" alt="Ekran Resmi 2025-07-11 19 44 15" src="https://github.com/user-attachments/assets/d4e7ab4b-924f-415a-8737-60632b4d54fe" />

<img width="1498" height="596" alt="Ekran Resmi 2025-07-11 19 44 25" src="https://github.com/user-attachments/assets/41ab9204-3d5d-4e71-9993-646abee5f99d" />

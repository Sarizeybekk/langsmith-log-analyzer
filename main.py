
import os
from dotenv import load_dotenv
import re
import json

from langsmith import traceable
from langchain_core.tracers import LangChainTracer

from agents.collector import CollectorAgent
from agents.llm_agent import LLMAgent
from agents.parser import ParserAgent
from agents.filter import FilterAgent
from agents.alert import AlertAgent
from agents.report import ReportAgent


load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"

collector = CollectorAgent()
llm_agent = LLMAgent()
parser = ParserAgent()
filter_agent = FilterAgent()
alert_agent = AlertAgent()
report_agent = ReportAgent()

@traceable(name="LogAnalysisRun")
def analyze_log(log_line):
    return llm_agent.analyze(log_line)


logs = collector.from_file()

for log in logs:
    print(f"\n🔍 Log analizi: {log}")
    llm_output = analyze_log(log)
    print("🧪 LLM çıktısı:", llm_output)

    try:
        parsed = json.loads(llm_output)
    except json.JSONDecodeError:
        json_matches = re.findall(r"\{[^{}]+\}", llm_output, re.DOTALL)
        if not json_matches:
            print("⚠Hiçbir geçerli JSON parçası bulunamadı. Atlaniyor.")
            continue
        try:
            parsed = json.loads(json_matches[0])
        except json.JSONDecodeError as e:
            print("JSON fallback da başarısız:", e)
            continue

    is_crit = filter_agent.is_critical(parsed, log_line=log)

    if is_crit:
        alert_agent.send_alert(log, parsed)
    else:
        print("Kritik değil.")

    parsed["is_critical"] = is_crit
    report_agent.update(parsed)
report_agent.summary()
report_agent.export()
report_agent.plot_charts()
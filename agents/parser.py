
import json

class ParserAgent:
    def parse(self, llm_output):
        try:
            return json.loads(llm_output)
        except json.JSONDecodeError as e:
            print("JSON parse hatası:", e)
            print("Girdi:", llm_output)
            return {}

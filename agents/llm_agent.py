from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

class LLMAgent:
    def __init__(self):
        self.llm = Ollama(model="llama3.2")

        self.prompt = PromptTemplate.from_template("""
Aşağıdaki log satırını analiz et:

"{log_line}"

Sadece **tek bir geçerli JSON nesnesi** döndür.  
Hiçbir açıklama, yorum, ekstra bilgi, ikinci JSON BLOĞU yazma.

Çıktı şu yapıda olmalı:

{{
  "event_type": "Login Failure, Disk Warning gibi kısa tanım",
  "source": "örn. rest.eys.fin.gate/v2/orders",
  "url_path": "örn. /eys/servis",
  "duration": 123,
  "timestamp": "2025-07-02 15:08:01",
  "has_error": true,
  "user_action_successful": false,
  "is_critical": true
}}
""")

        self.chain = self.prompt | self.llm

    def analyze(self, log_line):
        return self.chain.invoke({"log_line": log_line})

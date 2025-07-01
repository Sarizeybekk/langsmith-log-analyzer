
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

class LLMAgent:
    def __init__(self):
        self.llm = Ollama(model="llama3.2")
        self.prompt = PromptTemplate.from_template("""
Aşağadaki log satırını analiz et:

"{log_line}"

Yalnızca **tek bir geçerli JSON nesnesi** olarak yanıt ver.  
Hiçbir açıklama, yorum, ekstra bilgi, ikinci JSON BLOĞU yazma.

"event_type" alanı kısa ve genel bir olay tipi olmalıdır. 
IP adresi, kullanıcı adı gibi detaylar burada yer almamalıdır. 

Şu yapıda olsun:

{{
  "event_type": "Login Failure, Disk Warning",
  "has_error": true veya false,
  "user_action_successful": true veya false,
  "is_critical": true veya false
}}
""")
        self.chain = self.prompt | self.llm

    def analyze(self, log_line):
        return self.chain.invoke({"log_line": log_line})
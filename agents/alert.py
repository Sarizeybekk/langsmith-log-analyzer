
class AlertAgent:
    def send_alert(self, log_line, parsed):
        print("\n KRİTİK OLAY ALGILANDI!")
        print(f"Log: {log_line}")
        print(f"Detay: {parsed}")

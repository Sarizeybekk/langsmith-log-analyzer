
class FilterAgent:
    def is_critical(self, parsed, log_line=""):
        if parsed.get("is_critical") is True:
            return True

        keywords = [
            # Kimlik Doğrulama ve Yetkisizlik
            "failed login",
            "login failure",
            "multiple failed login",
            "unauthorized access",
            "unauthorized access attempt",
            "invalid credentials",
            "authentication failure",

            # Ağ ve Güvenlik
            "port scan",
            "ddos attack",
            "firewall breach",
            "suspicious activity",
            "intrusion detected",

            # Disk ve Donanım
            "disk space low",
            "disk warning",
            "raid array degraded",
            "hardware failure",

            # Veritabanı Hataları
            "connection timeout",
            "database timeout",
            "deadlock detected",
            "sql exception",

            # Uygulama Hataları
            "unhandled exception",
            "service unavailable",
            "crash report",
            "error while executing",

            # Diğer sistemsel problemler
            "out of memory",
            "kernel panic",
            "resource exhausted",
            "reboot required"
        ]

        log_line = log_line.lower()
        return any(kw in log_line for kw in keywords)
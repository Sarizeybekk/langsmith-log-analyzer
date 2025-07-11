import re

pattern = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}")
log_count = 0

with open("../logs/server.txt", "r", encoding="utf-8") as f:
    for line in f:
        if pattern.match(line):
            log_count += 1

print(f"Toplam log kaydı (tarih ile başlayan): {log_count}")

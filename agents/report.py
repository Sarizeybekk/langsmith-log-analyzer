import os
import json
import csv
from collections import Counter, defaultdict
from datetime import datetime
import matplotlib.pyplot as plt

class ReportAgent:
    def __init__(self):
        self.total_logs = 0
        self.critical_logs = 0
        self.non_critical_logs = 0
        self.events = []
        self.all_logs = []  # ✅ Zaman bazlı özet için gerekli

    def update(self, parsed):
        self.total_logs += 1
        if parsed.get("is_critical"):
            self.critical_logs += 1
        else:
            self.non_critical_logs += 1

        self.events.append(parsed.get("event_type", "Unknown"))
        self.all_logs.append(parsed)  # ✅ Saat bazlı raporlamaya dahil et

    def summary(self):
        print("\n📊 ANALİZ RAPORU")
        print(f"Toplam log sayısı       : {self.total_logs}")
        print(f"Kritik log sayısı       : {self.critical_logs}")
        print(f"Normal log sayısı       : {self.non_critical_logs}")
        print("Olay türleri:")
        for i, event in enumerate(self.events, start=1):
            print(f"  {i}. {event}")

    def export(self, path_json="results/report.json", path_csv="results/report.csv"):
        os.makedirs("results", exist_ok=True)

        with open(path_json, "w") as f:
            json.dump({
                "total_logs": self.total_logs,
                "critical_logs": self.critical_logs,
                "non_critical_logs": self.non_critical_logs,
                "events": self.events
            }, f, indent=2)

        with open(path_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Index", "Event Type"])
            for i, event in enumerate(self.events, 1):
                writer.writerow([i, event])

    def plot_charts(self):
        os.makedirs("results/charts", exist_ok=True)

        # Bar chart for event types
        counter = Counter(self.events)
        labels, counts = zip(*counter.items())

        plt.figure(figsize=(10, 5))
        plt.bar(labels, counts)
        plt.xticks(rotation=45, ha="right")
        plt.title("Olay Türü Dağılımı")
        plt.xlabel("Event Type")
        plt.ylabel("Adet")
        plt.tight_layout()
        plt.savefig("results/charts/event_type_distribution.png")
        plt.close()

        # Pie chart for critical vs normal
        plt.figure()
        plt.pie(
            [self.critical_logs, self.non_critical_logs],
            labels=["Kritik", "Normal"],
            autopct="%1.1f%%",
            startangle=140
        )
        plt.title("Kritik vs Normal Log Dağılımı")
        plt.axis("equal")
        plt.savefig("results/charts/critical_vs_normal.png")
        plt.close()

    def export_summary_table_by_interval(self, path="results/summary_by_hour.csv"):
        os.makedirs(os.path.dirname(path), exist_ok=True)

        summary = defaultdict(lambda: {
            "total": 0,
            "critical": 0,
            "errors": 0,
            "user_success": 0,
            "event_types": []
        })

        for log in self.all_logs:
            timestamp = log.get("timestamp", "")
            try:
                dt = datetime.strptime(timestamp[:13], "%Y-%m-%d %H")
                key = dt.strftime("%Y-%m-%d %H:00")
            except Exception:
                key = "Bilinmeyen"

            stats = summary[key]
            stats["total"] += 1
            if log.get("is_critical"):
                stats["critical"] += 1
            if log.get("has_error"):
                stats["errors"] += 1
            if log.get("user_action_successful"):
                stats["user_success"] += 1
            stats["event_types"].append(log.get("event_type", "Unknown"))

        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Saat", "Toplam Log", "Kritik Log", "Hatalı", "Kullanıcı Başarılı", "En Sık Olay"
            ])
            for hour, stats in sorted(summary.items()):
                most_common_event = Counter(stats["event_types"]).most_common(1)
                most_common_event_str = most_common_event[0][0] if most_common_event else "N/A"
                writer.writerow([
                    hour,
                    stats["total"],
                    stats["critical"],
                    stats["errors"],
                    stats["user_success"],
                    most_common_event_str
                ])

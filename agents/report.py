
class ReportAgent:
    def __init__(self):
        self.total_logs = 0
        self.critical_logs = 0
        self.non_critical_logs = 0
        self.events = []

    def update(self, parsed):
        self.total_logs += 1
        if parsed.get("is_critical"):
            self.critical_logs += 1
        else:
            self.non_critical_logs += 1

        self.events.append(parsed.get("event_type", "Unknown"))

    def summary(self):
        print("\nANALİZ RAPORU")
        print(f"Toplam log sayısı: {self.total_logs}")
        print(f"Kritik log sayısı: {self.critical_logs}")
        print(f"Normal log sayısı: {self.non_critical_logs}")
        print("Olay türleri:")
        for i, event in enumerate(self.events, start=1):
            print(f"  {i}. {event}")

    def export(self, path_json="results/report.json", path_csv="results/report.csv"):
        import json, csv, os
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
        import matplotlib.pyplot as plt
        from collections import Counter
        import os

        os.makedirs("results/charts", exist_ok=True)
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

        plt.figure()
        plt.pie([self.critical_logs, self.non_critical_logs],
                labels=["Kritik", "Normal"], autopct="%1.1f%%", startangle=140)
        plt.title("Kritik vs Normal Log Dağılımı")
        plt.axis("equal")
        plt.savefig("results/charts/critical_vs_normal.png")
        plt.close()




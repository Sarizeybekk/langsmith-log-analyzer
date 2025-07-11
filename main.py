import os
import re
import json
import hashlib
import time
from dotenv import load_dotenv
from rapidfuzz import fuzz
from concurrent.futures import ThreadPoolExecutor, as_completed
from langsmith import traceable
import csv
from agents.collector import CollectorAgent
from agents.llm_agent import LLMAgent
from agents.filter import FilterAgent
from agents.alert import AlertAgent
from agents.report import ReportAgent
from agents.anomaly import AnomalyAgent

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"

collector = CollectorAgent()
llm_agent = LLMAgent()
filter_agent = FilterAgent()
alert_agent = AlertAgent()
report_agent = ReportAgent()
anomaly_agent = AnomalyAgent()

PROCESSED_LOGS_FILE = "processed_labels.json"
SIMILARITY_THRESHOLD = 90
MAX_WORKERS = 6

if os.path.exists(PROCESSED_LOGS_FILE):
    with open(PROCESSED_LOGS_FILE, "r") as f:
        processed_logs = json.load(f)
else:
    processed_logs = {}

with open("config.json", "r") as f:
    config = json.load(f)

def parse_log_line(log_line, config):
    log_format = config.get("log_format", "custom")
    delimiter = config.get("delimiter", ";")
    encoding = config.get("encoding", "utf-8")
    ts_field = config.get("timestamp_field", "TIMESTAMP")
    service_field = config.get("service_field", "SERVICE")
    duration_field = config.get("duration_field", "DURATION")
    user_field = config.get("user_field", "USER")
    error_field = config.get("error_field", "ERROR")
    parsed = {}
    if log_format == "json":
        try:
            data = json.loads(log_line)
        except Exception:
            return {}
        parsed["timestamp"] = data.get(ts_field)
        parsed["service"] = data.get(service_field)
        parsed["duration"] = data.get(duration_field)
        parsed["user"] = data.get(user_field)
        parsed["error"] = data.get(error_field)
    elif log_format == "csv":
        reader = csv.DictReader([log_line], delimiter=delimiter)
        for row in reader:
            parsed["timestamp"] = row.get(ts_field)
            parsed["service"] = row.get(service_field)
            parsed["duration"] = row.get(duration_field)
            parsed["user"] = row.get(user_field)
            parsed["error"] = row.get(error_field)
    else:  # custom
        fields = dict(
            (kv.split("=", 1)[0].strip(), kv.split("=", 1)[1].strip())
            for kv in log_line.split(delimiter) if "=" in kv
        )
        parsed["timestamp"] = fields.get(ts_field)
        parsed["service"] = fields.get(service_field)
        parsed["duration"] = fields.get(duration_field)
        parsed["user"] = fields.get(user_field)
        parsed["error"] = fields.get(error_field)
    return parsed

def normalize_log(log):
    log = re.sub(r"\d{4}-\d{2}-\d{2}[\s,:.\d]+", "", log)
    log = re.sub(r"REQUESTID=[^;]+;", "", log)
    return log.strip()

def get_log_hash(log):
    norm = normalize_log(log)
    return hashlib.blake2b(norm.encode(), digest_size=16).hexdigest()

def should_skip(log):
    return "ERR=NONE" in log and "ERROR=" not in log

def is_error_log(log):
    return "ERROR=" in log or ": ERROR " in log

@traceable(name="LogAnalysisRun")
def analyze_log(log_line):
    return llm_agent.analyze(log_line)

def process_log(index_log_pair):
    index, log = index_log_pair
    print(f"\n[{index}/{total_logs}] log işleniyor...")

    if should_skip(log):
        print("Hata yok, atlanıyor.")
        return None

    start_time = time.time()

    log_hash = get_log_hash(log)
    norm_log = normalize_log(log)

    for old in processed_logs.values():
        if fuzz.ratio(norm_log, normalize_log(old["log"])) >= SIMILARITY_THRESHOLD:
            print(f" %{SIMILARITY_THRESHOLD}+ benzer log bulundu. LLM'e gönderilmiyor.")
            parsed = old["parsed"]
            parsed["is_critical"] = filter_agent.is_critical(parsed, log_line=log)
            return parsed

    try:
        llm_output = analyze_log(log)
        print("LLM çıktısı:", llm_output)

        parsed = json.loads(llm_output)
    except json.JSONDecodeError:
        json_matches = re.findall(r"\{[^{}]+\}", llm_output, re.DOTALL)
        if not json_matches:
            print("Geçerli JSON yok. Atlanıyor.")
            return None
        try:
            parsed = json.loads(json_matches[0])
        except:
            print("JSON fallback başarısız. Atlanıyor.")
            return None

    if not isinstance(parsed, dict):
        print("JSON değil. Atlanıyor.")
        return None

    processed_logs[log_hash] = {"log": log, "parsed": parsed}
    parsed["is_critical"] = filter_agent.is_critical(parsed, log_line=log)

    duration_ms = (time.time() - start_time) * 1000
    print(f"İşlem süre: {duration_ms:.2f} ms")
    return parsed

logs = collector.from_file()
parsed_logs = [parse_log_line(log, config) for log in logs]

logs = [log for log in logs if is_error_log(log)]
total_logs = len(logs)


with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(process_log, (i, log)) for i, log in enumerate(logs, 1)]
    for future in as_completed(futures):
        result = future.result()
        if result:
            report_agent.update(result)

with open(PROCESSED_LOGS_FILE, "w") as f:
    json.dump(processed_logs, f, indent=2)

report_agent.summary()
report_agent.export()
report_agent.plot_charts()
report_agent.export_summary_table_by_interval()

from datetime import datetime, timedelta
from collections import defaultdict, Counter

def extract_timestamp(log):
    match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})", log)
    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S,%f")
    return None

def extract_requestid(log):
    match = re.search(r"REQUESTID=([^;]+);", log)
    if match:
        return match.group(1)
    return None

def extract_duration(log):
    match = re.search(r"DURATION=(\d+);", log)
    if match:
        return int(match.group(1))
    return None

previous_time = None
log_time_deltas = []
for i, log in enumerate(logs, 1):
    current_time = extract_timestamp(log)
    if previous_time and current_time:
        delta = (current_time - previous_time).total_seconds() * 1000  # ms
        log_time_deltas.append(delta)
    previous_time = current_time
if log_time_deltas:
    print(f"\n[EK ANALİZ] Ortalama loglar arası süre farkı: {sum(log_time_deltas)/len(log_time_deltas):.2f} ms (min: {min(log_time_deltas):.2f}, max: {max(log_time_deltas):.2f})")

request_times = defaultdict(list)
for log in logs:
    ts = extract_timestamp(log)
    reqid = extract_requestid(log)
    if ts and reqid:
        request_times[reqid].append(ts)
request_durations = []
for reqid, times in request_times.items():
    if len(times) > 1:
        duration = (max(times) - min(times)).total_seconds() * 1000
        request_durations.append(duration)
if request_durations:
    print(f"[EK ANALİZ] Ortalama işlem (REQUESTID) süresi: {sum(request_durations)/len(request_durations):.2f} ms (min: {min(request_durations):.2f}, max: {max(request_durations):.2f})")

all_durations = [extract_duration(log) for log in logs if extract_duration(log) is not None]
if all_durations:
    print(f"[EK ANALİZ] DURATION ortalaması: {sum(all_durations)/len(all_durations):.2f} ms, max: {max(all_durations)} ms, min: {min(all_durations)} ms")
    threshold = 1000  # ms
    above_threshold = [d for d in all_durations if d > threshold]
    print(f"[EK ANALİZ] {threshold} ms üstü DURATION sayısı: {len(above_threshold)}")

time_buckets = Counter()
for log in logs:
    ts = extract_timestamp(log)
    if ts:
        bucket = ts.replace(second=0, microsecond=0)
        time_buckets[bucket] += 1
if time_buckets:
    most_common_time, most_common_count = time_buckets.most_common(1)[0]
    print(f"[EK ANALİZ] En yoğun dakika: {most_common_time} ({most_common_count} log)")

error_count = sum(1 for log in logs if is_error_log(log))
print(f"[EK ANALİZ] Toplam log: {len(logs)}, Hata içeren log: {error_count}, Hata oranı: {100*error_count/len(logs):.2f}%\n")

import matplotlib.pyplot as plt

error_messages = []
for log in logs:
    match = re.search(r"ERROR=([^;]+);", log)
    if match:
        error_messages.append(match.group(1).strip())
if error_messages:
    error_counter = Counter(error_messages)
    print("[EK ANALİZ] En çok görülen hata mesajları:")
    for msg, count in error_counter.most_common(5):
        print(f"  {msg}: {count} kez")

user_stats = defaultdict(lambda: {'total': 0, 'error': 0, 'duration_sum': 0, 'duration_count': 0})
for log in logs:
    user_match = re.search(r"USER=([^;]+);", log)
    user = user_match.group(1) if user_match else None
    if user:
        user_stats[user]['total'] += 1
        if is_error_log(log):
            user_stats[user]['error'] += 1
        dur = extract_duration(log)
        if dur is not None:
            user_stats[user]['duration_sum'] += dur
            user_stats[user]['duration_count'] += 1
if user_stats:
    print("[EK ANALİZ] Kullanıcıya özel istatistikler:")
    for user, stats in user_stats.items():
        avg_dur = stats['duration_sum']/stats['duration_count'] if stats['duration_count'] else 0
        print(f"  {user}: Toplam={stats['total']}, Hata={stats['error']}, Ortalama DURATION={avg_dur:.2f} ms")
else:
    print("[EK ANALİZ] Kullanıcı bilgisi bulunamadı.")

time_series = defaultdict(lambda: {'log': 0, 'error': 0})
for log in logs:
    ts = extract_timestamp(log)
    if ts:
        bucket = ts.replace(second=0, microsecond=0)
        time_series[bucket]['log'] += 1
        if is_error_log(log):
            time_series[bucket]['error'] += 1
if time_series:
    buckets = sorted(time_series.keys())
    log_counts = [time_series[b]['log'] for b in buckets]
    error_counts = [time_series[b]['error'] for b in buckets]
    plt.figure(figsize=(10,5))
    plt.plot(buckets, log_counts, label='Log Sayısı')
    plt.plot(buckets, error_counts, label='Hata Sayısı')
    plt.xlabel('Zaman (dakika)')
    plt.ylabel('Adet')
    plt.title('Zaman Serisi: Log ve Hata Sayısı')
    plt.legend()
    plt.tight_layout()
    plt.savefig('results/log_error_timeseries.png')
    print("[EK ANALİZ] Zaman serisi grafiği 'results/log_error_timeseries.png' olarak kaydedildi.")

if time_series:
    log_mean = sum(log_counts)/len(log_counts)
    log_std = (sum((x-log_mean)**2 for x in log_counts)/len(log_counts))**0.5
    anomaly_threshold = log_mean + 3*log_std
    anomalies = [(b, c) for b, c in zip(buckets, log_counts) if c > anomaly_threshold]
    if anomalies:
        print("[EK ANALİZ] Anomali tespiti: Beklenenden çok fazla log üretilen zaman dilimleri:")
        for b, c in anomalies:
            print(f"  {b}: {c} log (ortalama+3σ üstü)")
    else:
        print("[EK ANALİZ] Log yoğunluğunda belirgin bir anomali tespit edilmedi.")
    error_ratios = [e/l if l else 0 for e, l in zip(error_counts, log_counts)]
    error_mean = sum(error_ratios)/len(error_ratios)
    error_std = (sum((x-error_mean)**2 for x in error_ratios)/len(error_ratios))**0.5
    error_anomaly_threshold = error_mean + 3*error_std
    error_anomalies = [(b, r) for b, r in zip(buckets, error_ratios) if r > error_anomaly_threshold]
    if error_anomalies:
        print("[EK ANALİZ] Hata oranı anomalisi: Beklenenden yüksek hata oranı olan zaman dilimleri:")
        for b, r in error_anomalies:
            print(f"  {b}: {r*100:.2f}% hata oranı (ortalama+3σ üstü)")
    else:
        print("[EK ANALİZ] Hata oranında belirgin bir anomali tespit edilmedi.")

error_messages = []
for log in logs:
    match = re.search(r"ERROR=([^;]+);", log)
    if match:
        error_messages.append(match.group(1).strip())

from collections import defaultdict

time_series = defaultdict(lambda: 0)
for log in logs:
    ts = extract_timestamp(log)
    if ts:
        bucket = ts.replace(second=0, microsecond=0)
        time_series[bucket] += 1

if os.path.exists("anomaly_config.json"):
    with open("anomaly_config.json", "r") as f:
        anomaly_config = json.load(f)
    window_size = anomaly_config.get("window", 5)
    threshold = anomaly_config.get("threshold", 3.0)
else:
    window_size = 5
    threshold = 3.0

anomalies = anomaly_agent.detect_time_series_anomalies(time_series, window=window_size, threshold=threshold)
error_message_anomalies = anomaly_agent.detect_error_message_anomalies(error_messages, min_count=10)

if anomalies:
    print("[AGENT] Zaman serisi anomalileri:")
    for ts, count in anomalies:
        print(f"  {ts}: {count} log (kayan pencere anomali)")
else:
    print("[AGENT] Zaman serisinde anomali yok.")

if error_message_anomalies:
    print("[AGENT] Hata mesajı anomalileri:")
    for msg, count in error_message_anomalies:
        print(f"  {msg}: {count} kez")
else:
    print("[AGENT] Hata mesajı anomalisi yok.")

from collections import defaultdict
import numpy as np

duration_series = defaultdict(list)
for log in logs:
    ts = extract_timestamp(log)
    dur = extract_duration(log)
    if ts and dur is not None:
        bucket = ts.replace(second=0, microsecond=0)  # dakikalık
        duration_series[bucket].append(dur)

avg_duration_per_bucket = {b: sum(lst)/len(lst) for b, lst in duration_series.items() if lst}

buckets = sorted(avg_duration_per_bucket.keys())
values = np.array([avg_duration_per_bucket[b] for b in buckets])

duration_anomalies = []
for i in range(window_size-1, len(values)):
    window_slice = values[i-window_size+1:i+1]
    mean = np.mean(window_slice)
    std = np.std(window_slice)
    if std == 0:
        continue
    if values[i] > mean + threshold * std:
        duration_anomalies.append((buckets[i], values[i]))

if duration_anomalies:
    print("[DURATION ANOMALİ] Ortalama işlem süresi anomalileri:")
    for ts, val in duration_anomalies:
        print(f"  {ts}: {val:.2f} ms (ortalama+{threshold}σ üstü)")
else:
    print("[DURATION ANOMALİ] Anomali tespit edilmedi.")

report_data = {
    "error_messages": dict(Counter(error_messages)),
    "anomalies": [f"{ts}: {count} log (kayan pencere anomali)" for ts, count in anomalies],
    "error_message_anomalies": [f"{msg}: {count} kez" for msg, count in error_message_anomalies],
    "duration_anomalies": [f"{ts}: {val:.2f} ms (ortalama+{threshold}σ üstü)" for ts, val in duration_anomalies],
}

import os
report_path = "results/report.json"
if os.path.exists(report_path):
    import json
    with open(report_path, "r") as f:
        old_report = json.load(f)
    old_report.update(report_data)
    with open(report_path, "w") as f:
        json.dump(old_report, f, indent=2)
else:
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)

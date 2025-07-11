
from collections import Counter
import numpy as np

class AnomalyAgent:
    def __init__(self):
        self.anomalies = []
        self.error_message_anomalies = []

    def detect_time_series_anomalies(self, time_series, window=5, threshold=3.0):
        """
        Zaman serisi üzerinde kayan pencere ile anomali tespiti.
        Bir değerin, kendi penceresindeki ortalama + threshold * std'dan büyük olup olmadığına bakar.
        """
        buckets = sorted(time_series.keys())
        counts = np.array([time_series[b] for b in buckets])
        if len(counts) < window:
            return []
        anomalies = []
        for i in range(window - 1, len(counts)):
            window_slice = counts[i - window + 1:i + 1]
            mean = np.mean(window_slice)
            std = np.std(window_slice)
            if std == 0:
                continue  # Standart sapma sıfırsa anomaliye bakılmaz
            if counts[i] > mean + threshold * std:
                anomalies.append((buckets[i], counts[i]))
        self.anomalies = anomalies
        return anomalies

    def detect_error_message_anomalies(self, error_messages, min_count=10):
        # error_messages: list of error message strings
        counter = Counter(error_messages)
        anomalies = [(msg, count) for msg, count in counter.items() if count > min_count]
        self.error_message_anomalies = anomalies
        return anomalies
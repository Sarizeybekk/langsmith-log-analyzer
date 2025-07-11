import json
import difflib
from pathlib import Path

class LogCacheManager:
    def __init__(self, cache_path="processed_logs.jsonl", similarity_threshold=0.95):
        self.cache_path = Path(cache_path)
        self.similarity_threshold = similarity_threshold
        self.logs = []
        if self.cache_path.exists():
            with open(self.cache_path, "r") as f:
                self.logs = [line.strip() for line in f if line.strip()]

    def is_similar(self, new_log):
        for existing_log in self.logs:
            ratio = difflib.SequenceMatcher(None, new_log, existing_log).ratio()
            if ratio >= self.similarity_threshold:
                return True
        return False

    def add(self, new_log):
        self.logs.append(new_log)
        with open(self.cache_path, "a") as f:
            f.write(new_log.strip() + "\n")

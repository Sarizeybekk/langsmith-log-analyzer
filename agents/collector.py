
class CollectorAgent:
    def from_file(self, file_path="logs/logs.txt"):
        try:
            with open(file_path, "r") as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            print(f" Dosya bulunamadı: {file_path}")
            return []

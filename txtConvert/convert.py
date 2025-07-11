
import os
import shutil

def convert_log_to_txt(input_path: str, output_dir: str = "logs"):
    if not os.path.exists(input_path):
        print(f" File not found: {input_path}")
        return

    base = os.path.basename(input_path)
    name, _ = os.path.splitext(base)
    output_filename = f"{name}.txt"

    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, output_filename)

    shutil.copyfile(input_path, output_path)

    print(f"Converted to: {output_path}")

convert_log_to_txt("server.log")

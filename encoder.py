import base64
import sys


if __name__ == "__main__":
    script_file: str = sys.argv[1]
    compiled_file_path: str = "inject.bin"
    script: str
    encoded_script: bytes
    if len(sys.argv) < 2:
        print("Usage: encoder [script path]")
        exit(0)
    if len(sys.argv) > 2:
        compiled_file_path = sys.argv[2]
    with open(script_file, "r") as file:
        script = file.read()
        encoded_script = base64.b64encode(script.encode("utf-8"))
    with open(compiled_file_path, "wb") as file:
        file.write(encoded_script)

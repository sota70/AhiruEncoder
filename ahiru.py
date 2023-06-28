import json
import sys


def load_key_instructions(instruction_file_path: str):
    instructions: dict[str, str] = {}
    with open(instruction_file_path, "r") as file:
        instructions = json.load(file)
    return instructions


def compile_string_script(text: str, hex_instructions: dict[str, str]) -> bytes:
    decimal_script: list[int] = []
    for char in text:
        decimal_script.append(int(hex_instructions[char].split(",")[2], 16))
        decimal_script.append(int(hex_instructions[char].split(",")[0], 16))
    return bytes(decimal_script)


def compile_delay_script(milli_second: int) -> bytes:
    # NOTE: DELAY instructionは\x00の後に何ミリ秒遅延させるかを16進数で書く
    #       Ex) DELAY 100 -> \x00\x64
    decimal_script: list[int] = [0, milli_second]
    return bytes(decimal_script)


def compile_script(script_instructions: list[dict[str, str]],
                   hex_instructions: dict[str, str]) -> bytes:
    compiled_script: bytes = bytes()
    for instruction in script_instructions:
        if "STRING" in instruction.keys():
            compiled_script += compile_string_script(instruction["STRING"], hex_instructions)
            continue
        if "DELAY" in instruction.keys():
            compiled_script += compile_delay_script(int(instruction["DELAY"]))
            continue
    return compiled_script


def compile_raw_script(raw_script: str,
                       hex_instructions: dict[str, str]) -> bytes:
    return compile_script(parse_raw_script(raw_script), hex_instructions)


def parse_raw_script(raw_script: str) -> list[dict[str, str]]:
    instructions: list[dict[str, str]] = []
    command: str = ""
    arg: str = ""
    first_space_char_pos: int
    for line in raw_script.split("\n"):
        first_space_char_pos = line.find(" ")
        command = line.split(" ")[0]
        arg = line[first_space_char_pos + 1:]
        instructions.append({command: arg})
    return instructions


if __name__ == "__main__":
    script_file_path: str
    if len(sys.argv) < 2:
        print("Usage: python3 ahiru.py [script_file]")
        exit(1)
    script_file_path = sys.argv[1]
    hex_instructions: dict[str, str] = load_key_instructions(
        "instructions.json")
    with open(script_file_path, "r") as file:
        compiled_script = compile_raw_script(file.read(), hex_instructions)
        print(compiled_script)
    with open("inject.bin", "wb") as file:
        file.write(compiled_script)

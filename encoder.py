import json


def load_key_instructions(instruction_file_path: str):
    instructions: dict[str, str] = {}
    with open(instruction_file_path, "r") as file:
        instructions = json.load(file)
    return instructions


def compile_script(script_instructions: list[dict[str, str]],
                   hex_instructions: dict[str, str]) -> bytes:
    decimal_script: list[int] = []
    for instruction in script_instructions:
        if "STRING" not in instruction.keys():
            continue
        # NOTE: debug
        print(f"STRING: {instruction['STRING']}")
        for char in instruction["STRING"]:
            # NOTE: debug
            print(f"{char} bytes: ", end="")
            print(bytes([int(hex_instructions[char].split(",")[2], 16)]), end="")
            print(bytes([int(hex_instructions[char].split(",")[0], 16)]), end="")
            print()

            if char == " " or char == ",":
                continue
            decimal_script.append(
                int(hex_instructions[char].split(",")[2], 16))
            decimal_script.append(
                int(hex_instructions[char].split(",")[0], 16))
    return bytes(decimal_script)


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
    hex_instructions: dict[str, str] = load_key_instructions(
        "instructions.json")
    # NOTE:
    print(hex_instructions)
    with open("script.txt", "r") as file:
        compiled_script = compile_raw_script(file.read(), hex_instructions)
        print(compiled_script)
    with open("inject.bin", "wb") as file:
        file.write(compiled_script)

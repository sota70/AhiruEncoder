import json
import sys


'''
キーと16進のバイトコードとの対応表をロードして返す関数
対応表はjson形式で保存されている
Ex) { "H": "02,00,0b" }


param instruction_file_path: 対応表が保存されているpath

return: 対応表をdict[str, str]で返す
'''
def load_key_instructions(instruction_file_path: str):
    instructions: dict[str, str] = {}
    with open(instruction_file_path, "r") as file:
        instructions = json.load(file)
    return instructions


'''
キー入力命令(STRING)をバイトコードにエンコードする関数
キーとそれに対応する16進数の対応表を用いて、エンコードする
キー入力命令の場合はキーに対応するバイトコードを書くだけで
USBRubberDuckyがキー入力をしてくれる


param text: 入力する文字列
param hex_instructions: キーと16進数の対応表

return: エンコードされたバイトコードを返す
        Ex) b'\x0b\x02\x08\x00\x0f\x00\x0f\x00\x12\x00'
'''
def compile_string_script(text: str, hex_instructions: dict[str, str]) -> bytes:
    decimal_script: list[int] = []
    for char in text:
        # NOTE: キーに対応する16進数は3バイトで1セットであり、"h0,h1,h2"の形式で書かれている
        #       その中の0番と2番の16進数を取り出して、2番 -> 0番の順番で繋げる
        #       繋げたものをバイトコードにエンコードしたものが最終的な結果となる
        decimal_script.append(int(hex_instructions[char].split(",")[2], 16))
        decimal_script.append(int(hex_instructions[char].split(",")[0], 16))
    return bytes(decimal_script)


'''
遅延命令(DELAY)をバイトコードにエンコードする関数


param milli_second: 遅延する時間(ミリ秒)

return: エンコードしたバイトーコード
        Ex) DELAY 100 -> \x00\x64
'''
def compile_delay_script(milli_second: int) -> bytes:
    # NOTE: DELAY instructionは\x00の後に何ミリ秒遅延させるかを16進数で書く
    #       Ex) DELAY 100 -> \x00\x64
    decimal_script: list[int] = []
    instruction_code: int = 0
    delay: int = int(milli_second)
    full_delay: int = 255
    full_delay_count: int = -1
    if delay < 256:
        return bytes([instruction_code, delay])
    # NOTE: バイトコードは1バイトに0~255までの数しか表現できない
    #       そこで、複数の遅延命令に分ける
    #       遅延が255以下になるまで、255ミリ秒の遅延命令をする
    #       遅延が255以下になったら、その値で遅延命令をして終わる
    #       Ex) 1000ミリ秒の遅延の場合
    #           255ミリ秒の遅延を3回した後、余った235ミリ秒で遅延をする
    full_delay_count = int(delay / 255)
    for i in range(full_delay_count):
        decimal_script.append(instruction_code)
        decimal_script.append(full_delay)
    decimal_script.append(instruction_code)
    decimal_script.append(delay - full_delay * full_delay_count)
    return bytes(decimal_script)


'''
命令とその命令に付いてくる引数を基に、スクリプトをエンコードする関数
USBRubberDuckyのスクリプトでは、１つの命令と１つの引数で1セットとなる
Ex) DELAY 100
左が命令で、右が引数


param script_instructions: 命令とその命令に付いてくる引数の対応表
                           Ex) [{"DELAY": 100}, {"STRING": "Hello, World"}]
param hex_instructions: キー入力とそれに対応する16進数の対応表
                        STRING命令をエンコードするときに使う
return: エンコードしたバイトコードを返す
'''
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


'''
USBRubberDuckyスクリプトをエンコードして、バイトコードを返す関数
生のスクリプトを辞書形式にしてから、compile_script関数を使って最終的にバイトコードにする


param raw_script: 生の状態のスクリプト
param hex_instructions: キー入力と16進数の対応表
                        STRING命令で使う
return: エンコードされたバイトコードを返す
'''
def compile_raw_script(raw_script: str,
                       hex_instructions: dict[str, str]) -> bytes:
    return compile_script(parse_raw_script(raw_script), hex_instructions)


'''
引数に渡されたスクリプトを辞書形式にして、扱いやすい形式にする関数
Ex) DELAY 100
    STRING Hello, World
    ↓
    [{"DELAY": 100}, {"STRING": "Hello, World"}]


param raw_script: 生のスクリプト

return: 辞書形式になったスクリプトを返す
'''
def parse_raw_script(raw_script: str) -> list[dict[str, str]]:
    instructions: list[dict[str, str]] = []
    command: str = ""
    arg: str = ""
    comment_out_instruction: str = "REM"
    first_space_char_pos: int
    for line in raw_script.split("\n"):
        if line == "\n" or line.startswith(comment_out_instruction):
            continue
        first_space_char_pos = line.find(" ")
        command = line.split(" ")[0]
        # NOTE: 命令と引数は、最初の空白文字で区切られる
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

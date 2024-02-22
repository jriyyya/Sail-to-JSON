import re
import os
import json

def remove_comments(text):
    pattern = r'/\*.*?\*/|//.*?$'
    return re.sub(pattern, '', text, flags=re.MULTILINE)

def substring_until_last_occurrence(input_string, word):
    last_index = input_string.rfind(word)
    if last_index != -1:
        return input_string[:last_index]
    else:
        return input_string

def extract_instruction_details(file_path):
    with open(file_path, "r") as file:
        content = file.read()

    content = remove_comments(content)

    instructions = dict()

    pattern = r'mapping\s+(\w+)_mnemonic\s+:\s+(\w+)\s+<->\s+(\w+)\s+=\s+{([^}]*)}'

    matches = re.findall(pattern, content, re.MULTILINE)

    for match in matches:
        lines = [l.strip() for l in (match[3].split("\n"))]
        for line in lines:
            parts = line.split("<->")
            if len(parts) == 2:
                name = parts[0].replace(" ","")
                mnemonic = parts[1].replace(",","").replace('"',"").replace(" ","")
                instructions[name] = {"mnemonic": mnemonic}

    pattern = r'mapping\s+clause\s+assembly\s*=\s*(\w+)\(.*?\)\s*<->\s*"(\w+)"'
    matches = re.findall(pattern, content, re.MULTILINE)

    for match in matches:
        instructions[match[0]] = { "mnemonic": match[1]}

    for name in instructions.keys():
        for line in content.split("\n"):
            if "mapping clause encdec" in line and name in line:
                    encdec_begin = content.find("<->", content.find(line))
                    encdec_def = substring_until_last_occurrence(content[encdec_begin:].split("\n")[0].replace("<->", "").replace(" ",""), "@").split("@")
                    # print(name, encdec_def)
                    if name in instructions:
                        print(name, encdec_def)
                        instructions[name]["operands"] = encdec_def

    if len(instructions) > 0:
        return instructions


def find_sail_files(folder_path):
    sail_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".sail"):
                sail_files.append(os.path.join(root, file))
    return sail_files

def main(folder_path, output_file, extraction_method):
    all_instructions = {"instructions":{}}
    sail_files = find_sail_files(folder_path)
    for file_path in sail_files:
        print(file_path,end="\n\n")
        instruction_info = extraction_method(file_path)
        if instruction_info:
            for instr in instruction_info:
                all_instructions["instructions"][instr] = (instruction_info[instr])

    with open(output_file, "w") as json_file:
        json.dump(all_instructions, json_file, indent=4)


folder_path = "base"
output_file = "ISA.json"

main(folder_path, output_file, extract_instruction_details)

from flask import Flask, request, jsonify
import re

app = Flask(__name__)

def remove_comments(text):
    pattern = r'/\*.*?\*/|//.*?$'
    return re.sub(pattern, '', text, flags=re.MULTILINE)

def extract_instruction_details(file_content):
    content = remove_comments(file_content)

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
                if name in instructions:
                    instructions[name]["operands"] = encdec_def

    return instructions if instructions else None

@app.route('/extract_instructions', methods=['POST'])
def extract_instructions():
    file_content = request.data.decode('utf-8')
    instruction_info = extract_instruction_details(file_content)
    if instruction_info:
        return jsonify({"instructions":instruction_info})
    else:
        return jsonify({"error": "No instructions found"}), 404

def substring_until_last_occurrence(input_string, word):
    last_index = input_string.rfind(word)
    if last_index != -1:
        return input_string[:last_index]
    else:
        return input_string

if __name__ == '__main__':
    app.run(debug=True)

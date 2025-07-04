import json
import re

input_file_path = "data/documents.jsonl"
output_file_path = "data/documents_edited.jsonl"

with open(input_file_path, "r") as input_file, open(output_file_path, "w") as output_file:
    for line in input_file:
        line_data = json.loads(line)
        text = line_data.get("text")
        text = (text[text.find("Gesamtzeit"):text.find("Rezept von")])

        # saetze = re.findall(r'.*?\. ?', text)
        
        saetze = re.split(r'(?<=[.!?]) +', text)
        print(saetze)
        char_amount = sum(len(satz) for satz in saetze)

        while char_amount > 500:
            del saetze[-1]
            char_amount = sum(len(satz) for satz in saetze)
        text_output = "".join(saetze)

        line_data["text_visible"] = text_output
        output_file.write(json.dumps(line_data) + "\n")

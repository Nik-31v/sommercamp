import json
from tqdm import tqdm

doc_to_title = {}

with open ("data/documents.jsonl") as f:
    for line in f:
        line = json.loads(line)
        doc_to_title[line["docno"]] = line["title"].split("|")[0].split("von")[0].strip()

def build_llm_request(title):
    return "Du bist ein Koch der Spezialisiert auf Apfelgerichte ist. " + \
            "Überprüfe inwiefern die Zutat Apfel von Folgendem Gericht im Vordergrund steht und beurteile auf einer Skala von 1 " + \
            "(kein Apfel oder gerichte wo apfel nur im namen vorkommt) bis 10 (Apfel steht voll im Vordergrund).\n\n" + \
            "Das gericht ist: \"" + title + "\"\n\n" + \
            "Antworte in json mit zwei Feldern, Begründung (200 Zeichen) und Bewertung."

with open("data/apple-scores.jsonl", "w") as f:
    for doc, title in tqdm(doc_to_title.items()):
        llm_request = build_llm_request(title)
        llm_response = {"Begründung": "hallo", "Wert": 0}
        f.write(json.dumps({"docno": doc, "title": title, "llm_request": llm_request, "llm_response": llm_response})+ "\n")
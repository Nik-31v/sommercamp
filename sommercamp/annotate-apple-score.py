import json
from tqdm import tqdm

doc_to_title = {}

with open ("data/documents.jsonl") as f:
    for line in f:
        line = json.loads(line)
        doc_to_title[line["docno"]] = line["title"].split("|")[0].split("von")[0].strip()

def get_llm_response(request, llm):
    from openai import OpenAI as cli
    messages = []
    messages.append({"role": "user", "content": request})

    output = cli().chat.completions.create(model=llm, messages=messages)

    return output.choices[0].message.to_dict()

def build_llm_request(title):
    return "Du bist ein Koch der Spezialisiert auf Apfelgerichte ist. " + \
            "Überprüfe inwiefern die Zutat Apfel von Folgendem Gericht im Vordergrund steht und beurteile auf einer Skala von 1 " + \
            "(kein Apfel oder gerichte wo apfel nur im namen vorkommt) bis 10 (Apfel steht voll im Vordergrund).\n\n" + \
            "Das gericht ist: \"" + title + "\"\n\n" + \
            "Antworte in json mit zwei Feldern, Begründung (200 Zeichen) und Bewertung."

with open("data/apple-scores.jsonl", "w") as f:
    for doc, title in tqdm(doc_to_title.items()):
        llm_request = build_llm_request(title)
        llm_response = get_llm_response(llm_request, "o4-mini")
        f.write(json.dumps({"docno": doc, "title": title, "llm_request": llm_request, "llm_response": llm_response})+ "\n")

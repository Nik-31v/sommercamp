# Hier importieren wir die benötigten Softwarebibliotheken.
from os.path import abspath, exists
from sys import argv
from streamlit import (text_input, header, title, subheader,
    container, markdown, link_button, divider, set_page_config, slider, badge)
from pyterrier import started, init
# Die PyTerrier-Bibliothek muss zuerst gestartet werden,
# um alle seine Bestandteile importieren zu können.
if not started():
    init()
from pyterrier import IndexFactory
from pyterrier.batchretrieve import BatchRetrieve
from pyterrier.text import get_text
import json


apple_scores = {}  # Leeres Dictionary zum Speichern der Bewertungen

# Öffne die Datei mit den Bewertungen (JSONL = JSON pro Zeile)
with open("data/apple-scores.jsonl", "r") as f:
    for line_num, line in enumerate(f, start=1):  # Zähle mit, in welcher Zeile wir sind
        try:
            l = json.loads(line)  # Lade die aktuelle Zeile als JSON-Daten
            
            # Versuche, den content-String aus dem "llm_response"-Feld zu bekommen
            content = l.get("llm_response", {}).get("content", "")
            
            if content:
                # Wenn content nicht leer ist, versuche ihn als JSON zu interpretieren
                parsed = json.loads(content)
                
                # Hole den Wert für "Bewertung" aus dem JSON-Objekt
                bewertung = parsed.get("Bewertung")
                
                if bewertung is not None:
                    # Speichere die Bewertung als Ganzzahl in apple_scores
                    apple_scores[l["docno"]] = int(bewertung)
                else:
                    # Hinweis, wenn "Bewertung" fehlt
                    print(f"[Zeile {line_num}] No element 'Bewertung' in content: {content}")
            else:
                # Hinweis, wenn "content" leer oder fehlt
                print(f"[Zeile {line_num}] Empty or missing 'content'")
        
        except Exception as e:
            # Fange alle Fehler ab (z. B. JSONDecodeError, KeyError, TypeError, etc.)
            print(f"[Zeile {line_num}] Error while processing: {e}")


# Diese Funktion baut die App für die Suche im gegebenen Index auf.
def app(index_dir) -> None:

    # Konfiguriere den Titel der Web-App (wird im Browser-Tab angezeigt)
    set_page_config(
        page_title="Schul-Suchmaschine",
        layout="centered",
    )

    # Gib der App einen Titel und eine Kurzbeschreibung:
    title("Schul-Suchmaschine")
    markdown("Hier kannst du unsere neue Schul-Suchmaschine nutzen:")
    divider()

    # Erstelle ein Text-Feld, mit dem die Suchanfrage (query)
    # eingegeben werden kann.
    query = text_input(
        label="Suchanfrage",
        placeholder="Suche...",
        value="",
    )

    apple_score = slider("Apfelgehalt", 0, 10, 8)
    markdown("Apfelgehalt: " + str(apple_score))


    # Wenn die Suchanfrage leer ist, dann kannst du nichts suchen.
    if query == "":
        markdown("Bitte gib eine Suchanfrage ein.")
        return

    # Öffne den Index.
    index = IndexFactory.of(abspath(index_dir))
    # Initialisiere den Such-Algorithmus.
    searcher = BatchRetrieve(
        index,
        wmodel="BM25",
        num_results=1000,
    )
    # Initialisiere das Modul, zum Abrufen der Texte.
    text_getter = get_text(index, metadata=["url", "title", "text"])
    # Baue die Such-Pipeline zusammen.
    pipeline = searcher >> text_getter
    # Führe die Such-Pipeline aus und suche nach der Suchanfrage.
    results = pipeline.search(query)

    # Zeige eine Unter-Überschrift vor den Suchergebnissen an.
    divider()
    header("Suchergebnisse")

    # Wenn die Ergebnisliste leer ist, gib einen Hinweis aus.
    if len(results) == 0:
        markdown("Keine Suchergebnisse.")
        return

    results_filtered = []
    # Gib nun der Reihe nach, alle Suchergebnisse aus.
    for _, row in results.iterrows():
        # Pro Suchergebnis, erstelle eine Box (container).
        with container(border=True):
            r = row.to_dict()
            r["Apfelgehalt"] = apple_scores.get(r["docno"], -1)
            if r["Apfelgehalt"] < apple_score:
                continue
            results_filtered.append(r)

    # Wenn es Suchergebnisse gibt, dann zeige an, wie viele.
    markdown(f"{len(results_filtered)} Möglichkeiten, für deinen täglichen Apfel.")

    # Gib nun der Reihe nach, alle Suchergebnisse aus.
    for row in results_filtered:
        # Pro Suchergebnis, erstelle eine Box (container).
        with container(border=True):
            # Zeige den Titel der gefundenen Webseite an.
            subheader(row["title"])
            badge("Apfelgehalt: " + str(row["Apfelgehalt"]), color="green")
            # Speichere den Text in einer Variablen (text).
            text = row["text"]
            # Schneide den Text nach 500 Zeichen ab.
            text = text[:500]
            # Ersetze Zeilenumbrüche durch Leerzeichen.
            text = text.replace("\n", " ")
            # Zeige den Dokument-Text an.
            markdown(text)
            # Gib Nutzern eine Schaltfläche, um die Seite zu öffnen.
            link_button("Seite öffnen", url=row["url"])


# Die Hauptfunktion, die beim Ausführen der Datei aufgerufen wird.
def main():
    # Lade den Pfad zum Index aus dem ersten Kommandozeilen-Argument.
    index_dir = argv[1]

    # Wenn es noch keinen Index gibt, kannst du die Suchmaschine nicht starten.
    if not exists(index_dir):
        exit(1)

    # Rufe die App-Funktion von oben auf.
    app(index_dir)


if __name__ == "__main__":
    main()
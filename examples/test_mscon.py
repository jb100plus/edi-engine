from pathlib import Path

from edifact.engine.edifact_engine import EdifactEngine

BASE_PATH = Path(__file__).resolve().parents[1] / "edifact" / "grammars"

def main():
    # Datei einlesen
    #edi_path = Path(__file__).resolve().parent / "mscons_sample.edi"
    edi_path = Path(__file__).resolve().parent / "bhkw.edi"
    lines = edi_path.read_text(encoding="utf-8").splitlines()

    # Engine bauen
    engine = EdifactEngine(str(BASE_PATH))

    # Nachricht verarbeiten
    message = engine.process_message(lines)

    print("=== Parsed MSCONS ===")
    print(message)

if __name__ == "__main__":
    main()

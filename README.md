# edi-engine

Eine Python-Bibliothek zum Laden, Prüfen und Verarbeiten von EDIFACT-Nachrichten. Die Engine verwendet YAML-basierte Zustandsautomaten (FSM), Segmentgrammatiken und Actions, sodass Nachrichtentypen getrennt und erweiterbar definiert werden können.

## Funktionen

- Erkennung des EDIFACT-Nachrichtentyps über das `UNH`-Segment
- Laden von FSM, Segmentdefinitionen und Actions aus YAML-Dateien
- Verarbeiten von Nachrichtenzeilen oder zusammenhängenden EDIFACT-Segmentströmen
- Unterstützung mehrerer Nachrichten innerhalb einer Datei
- Validierung von Segmentwiederholungen sowie Pflichtsegmenten
- Validierung von Datenelementen und Composite-Elementen
- Verarbeitung des MSCONS-Nachrichtentyps
- Export von MSCONS-Verbrauchsdaten als CSV beziehungsweise pandas DataFrame
- Grafische Darstellung der MSCONS-Zustandsmaschine

## Unterstützte Nachrichtentypen

Die Registry enthält derzeit folgende Einträge:

- `MSCONS` – Metered Services Consumption Report
- `UTILMD` – Nachricht zur Änderung von Markt- und Stammdaten
- `INVOIC` – Rechnungsnachricht

Die konkreten Grammatikdateien befinden sich unter `edifact/grammars`.

## Projektstruktur

```text
edifact/
  engine/
    edifact_engine.py       Zentrale Engine
    fsm_engine.py           Zustandsautomaten-Ausführung
    validator.py            Grammatik- und Wiederholungsprüfung
    actions/                Aktionen für Nachrichtenarten
    loader/                 YAML- und Registry-Lader
    parser/                 Parser für Segmente und UNH
  grammars/
    registry.yaml           Zuordnung der Nachrichtentypen
    fsm/                    Zustandsautomaten
    segments/               Segmentdefinitionen
    actions/                Zusätzliche Action-Definitionen
examples/
  bhkw.edi                  Beispiel mit drei MSCONS-Nachrichten
  mscons_sample.edi         Kleine MSCONS-Beispieldatei
  test_mscon.py             Einfacher MSCONS-Testlauf
  export_mscons_csv.py      Export der Verbrauchsdaten als CSV
```

## Installation

Voraussetzung ist Python 3.10 oder neuer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Zusätzlich wird für den CSV-Export `pandas` benötigt:

```bash
pip install pandas
```

## Verwendung

Eine EDIFACT-Datei kann mit der Engine verarbeitet werden:

```python
from pathlib import Path

from edifact.engine.edifact_engine import EdifactEngine

base_path = "edifact/grammars"
lines = Path("examples/mscons_sample.edi").read_text(
    encoding="utf-8"
).splitlines()

engine = EdifactEngine(base_path)
message = engine.process_message(lines)

print(message)
```

Das Ergebnis enthält die Abschnitte `header`, `body` und `trailer`.

## MSCONS-CSV-Export

Das Beispiel `examples/bhkw.edi` enthält drei MSCONS-Nachrichten. Das Exportskript trennt die Nachrichten, liest die Messwerte und Zeitintervalle und erzeugt folgende Dateien:

- `bhkw_mscons_1.csv`
- `bhkw_mscons_2.csv`
- `bhkw_mscons_3.csv`
- `bhkw_mscons_all.csv`

Ausführen:

```bash
python examples/export_mscons_csv.py
```

Die CSV-Dateien enthalten unter anderem:

- Nachrichtennummer
- Belegnummer
- Messlokation
- Positions- und Artikelnummer
- Start- und Endzeitpunkt des Intervalls
- Menge
- Einheit
- Mengenqualifizierer

Die Zeitpunkte werden aus den `DTM`-Segmenten übernommen und als ISO-8601-Werte ausgegeben.

## Parser und Validierung

Der `SegmentParser` zerlegt ein EDIFACT-Segment in:

- Segmenttag
- Datenelemente
- Komponenten zusammengesetzter Datenelemente

Dabei werden EDIFACT-Escapezeichen wie `?+`, `?:` und `?'` berücksichtigt.

Der `SegmentValidator` prüft unter anderem:

- Mindest- und Höchstanzahl von Segmenten
- Pflichtsegmente anhand von `min_repeat`
- Pflichtdatenelemente und Komponenten
- Mindest- und Höchstlängen

## Mehrere Nachrichten in einer Datei

Die Engine akzeptiert aktuell zusammenhängende Segmentströme sowie Zeilenlisten. Für Datei-Container trennt das Exportskript alle Bereiche zwischen `UNH` und `UNT` und verarbeitet jeden Bereich einzeln.

## Einschränkungen

- Die Segmentgrammatiken sind noch keine vollständige Implementierung aller EDIFACT-Spezifikationen.
- Die FSM-Dateien prüfen derzeit hauptsächlich den Segmentablauf, nicht alle fachlichen Geschäftsregeln.
- EDIFACT-Syntaxvarianten werden schrittweise ergänzt.
- Die erzeugten CSV-Dateien sind Beispiele und können je nach MSCONS-Variante zusätzliche Spalten benötigen.

## Tests

Der vorhandene MSCONS-Test kann direkt ausgeführt werden:

```bash
python examples/test_mscon.py
```

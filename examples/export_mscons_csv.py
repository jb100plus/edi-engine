from pathlib import Path

import pandas as pd

from edifact.engine.edifact_engine import EdifactEngine
from edifact.engine.parser.segment_parser import SegmentParser

BASE_PATH = Path(__file__).resolve().parents[1] / "edifact" / "grammars"
EDI_PATH = Path(__file__).resolve().parent / "bhkw.edi"
OUTPUT_DIR = Path(__file__).resolve().parent


def split_segment_stream(text: str) -> list[str]:
    """Teilt einen EDIFACT-Strom in einzelne Segmente auf."""
    segments = []
    start = 0

    for index, char in enumerate(text):
        if char == "'" and (index == 0 or text[index - 1] != "?"):
            segment = text[start:index].strip()
            if segment:
                segments.append(segment)
            start = index + 1

    remainder = text[start:].strip()
    if remainder:
        segments.append(remainder)

    return segments


def split_messages(text: str) -> list[list[str]]:
    """Extrahiert alle UNH ... UNT-Nachrichten aus einem Strom."""
    segments = split_segment_stream(text)
    messages = []
    current = None

    for raw_segment in segments:
        tag = raw_segment.split("+", 1)[0]

        if tag == "UNH":
            current = [raw_segment]
        elif current is not None:
            current.append(raw_segment)
            if tag == "UNT":
                messages.append(current)
                current = None

    return messages


def component(segment: dict, element_index: int, component_index: int = 0):
    try:
        return segment["elements"][element_index][component_index]
    except (IndexError, KeyError, TypeError):
        return None


def element(segment: dict, element_index: int):
    try:
        return segment["elements"][element_index]
    except (IndexError, KeyError, TypeError):
        return []


def unescape(value: str | None) -> str | None:
    if value is None:
        return None
    return (
        value.replace("??", "?")
        .replace("?+", "+")
        .replace("?:", ":")
        .replace("?'", "'")
    )


def format_datetime(value: str | None, offset: str | None = None) -> str | None:
    value = unescape(value)
    if value is None:
        return None

    offset_from_value = None
    if "+" in value:
        date_value, offset_from_value = value.rsplit("+", 1)
    else:
        date_value = value

    if len(date_value) == 12:
        result = f"{date_value[:4]}-{date_value[4:6]}-{date_value[6:8]}T{date_value[8:10]}:{date_value[10:12]}:00"
    else:
        return value

    timezone_offset = offset or offset_from_value
    if timezone_offset:
        timezone_offset = unescape(timezone_offset).strip()
        if len(timezone_offset) == 2 and timezone_offset.isdigit():
            return f"{result}+{timezone_offset}:00"
    return result


def message_to_rows(message: dict, raw_message: list[str]) -> list[dict]:
    """Wandelt eine MSCONS-Nachricht in Verbrauchszeilen um."""
    header = message["header"]
    unh = header.get("UNH", {})
    bgm = header.get("BGM", {})

    message_number = element(unh, 0)[0] if element(unh, 0) else None
    document_number = element(bgm, 1)[0] if element(bgm, 1) else None

    location = None
    line_number = None
    item_type = None
    item_number = None
    item_version = None
    interval_start = None
    interval_end = None
    rows = []

    parser = SegmentParser()
    segments = [parser.parse_segment(raw_segment) for raw_segment in raw_message]

    for segment in segments:
        tag = segment["tag"]

        if tag == "LOC":
            location = unescape(element(segment, 1)[0] if len(element(segment, 1)) else None)

        elif tag == "LIN":
            line_number = unescape(element(segment, 0)[0] if element(segment, 0) else None)

        elif tag == "PIA":
            item_type = unescape(element(segment, 0)[0] if element(segment, 0) else None)
            item_parts = element(segment, 1)
            if item_parts:
                item_number = unescape(item_parts[0])
                item_version = unescape(item_parts[1] if len(item_parts) > 1 else None)

        elif tag == "DTM":
            qualifier = component(segment, 0, 0)
            dtm_value = component(segment, 0, 1)
            dtm_format = component(segment, 0, 2)
            if qualifier == "163":
                interval_start = format_datetime(dtm_value)
            elif qualifier == "164":
                interval_end = format_datetime(dtm_value)

        elif tag == "QTY":
            qualifier = component(segment, 0, 0)
            if qualifier != "220":
                continue

            quantity = unescape(component(segment, 0, 1))
            unit = unescape(component(segment, 0, 2))
            rows.append(
                {
                    "message_number": message_number,
                    "document_number": document_number,
                    "location": location,
                    "line_number": line_number,
                    "item_type": item_type,
                    "item_number": item_number,
                    "item_version": item_version,
                    "interval_start": interval_start,
                    "interval_end": interval_end,
                    "quantity": float(quantity) if quantity is not None else None,
                    "unit": unit,
                    "quantity_qualifier": qualifier,
                }
            )

    return rows


def main():
    text = EDI_PATH.read_text(encoding="utf-8")
    engine = EdifactEngine(str(BASE_PATH))
    all_rows = []

    for index, raw_message in enumerate(split_messages(text), start=1):
        parsed = engine.process_message(raw_message)
        rows = message_to_rows(parsed, raw_message)

        frame = pd.DataFrame(rows)
        csv_path = OUTPUT_DIR / f"bhkw_mscons_{index}.csv"
        frame.to_csv(csv_path, index=False, encoding="utf-8")

        all_rows.extend(rows)
        print(f"{csv_path.name}: {len(frame)} Verbrauchszeilen")

    combined = pd.DataFrame(all_rows)
    combined_path = OUTPUT_DIR / "bhkw_mscons_all.csv"
    combined.to_csv(combined_path, index=False, encoding="utf-8")
    print(f"{combined_path.name}: {len(combined)} Verbrauchszeilen")


if __name__ == "__main__":
    main()

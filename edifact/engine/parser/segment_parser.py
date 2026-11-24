class SegmentParser:
    """
    Universeller EDIFACT-Segmentparser.
    Zerlegt eine Segmentzeile in:
    - Segmentname
    - Datenelemente
    - Composite-Elemente
    """

    def __init__(self, segment_terminator="'", element_separator="+", component_separator=":"):
        self.segment_terminator = segment_terminator
        self.element_separator = element_separator
        self.component_separator = component_separator

    # ---------------------------------------------------------
    # Hauptmethode: Segment parsen
    # ---------------------------------------------------------
    def parse_segment(self, raw_line):
        """
        raw_line: z.B. "MEA+AAE+KWH:3.5'"
        Rückgabe: dict mit:
        {
            "tag": "MEA",
            "elements": [
                ["AAE"],
                ["KWH", "3.5"]
            ]
        }
        """

        # Segmentterminator entfernen
        line = raw_line.strip()
        if line.endswith(self.segment_terminator):
            line = line[:-1]

        # Split in Tag + Elemente; escaped + bleibt Dateninhalt
        parts = self._split_unescaped(line, self.element_separator)
        tag = parts[0]
        elements = parts[1:]

        parsed_elements = []
        for el in elements:
            if self.component_separator in el:
                parsed_elements.append(el.split(self.component_separator))
            else:
                parsed_elements.append([el])

        return {
            "tag": tag,
            "elements": parsed_elements
        }

    def _split_unescaped(self, text, separator):
        parts = []
        start = 0

        for index, char in enumerate(text):
            if char == separator and (index == 0 or text[index - 1] != "?"):
                parts.append(text[start:index])
                start = index + 1

        parts.append(text[start:])
        return parts

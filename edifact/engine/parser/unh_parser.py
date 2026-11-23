class UNHParser:
    """
    Parser für das UNH-Segment.
    Extrahiert den Nachrichtentyp (z.B. MSCONS) und optional Version/Release.
    """

    def extract_message_type(self, unh_segment):
        """
        unh_segment: dict aus SegmentParser:
        {
            "tag": "UNH",
            "elements": [
                ["1"],
                ["MSCONS", "D", "96A", "UN"]
            ]
        }

        Rückgabe: "MSCONS"
        """

        if unh_segment["tag"] != "UNH":
            raise ValueError("Kein UNH-Segment übergeben")

        elements = unh_segment.get("elements", [])

        if len(elements) < 2:
            raise ValueError("UNH-Segment unvollständig")

        # UNH+<ref>+<message_type>:<version>:<release>:<agency>
        message_def = elements[1]

        if len(message_def) == 0:
            raise ValueError("UNH enthält keinen Nachrichtentyp")

        message_type = message_def[0]
        return message_type

    def extract_full_info(self, unh_segment):
        """
        Optional: vollständige UNH-Informationen extrahieren.
        Rückgabe:
        {
            "type": "MSCONS",
            "version": "D",
            "release": "96A",
            "agency": "UN"
        }
        """

        elements = unh_segment.get("elements", [])
        message_def = elements[1]

        return {
            "type": message_def[0] if len(message_def) > 0 else None,
            "version": message_def[1] if len(message_def) > 1 else None,
            "release": message_def[2] if len(message_def) > 2 else None,
            "agency": message_def[3] if len(message_def) > 3 else None,
        }

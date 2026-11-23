class ElementParser:
    """
    Universeller EDIFACT-Elementparser.
    Zerlegt ein einzelnes Datenelement in Komponenten.
    """

    def __init__(self, component_separator=":"):
        self.component_separator = component_separator

    # ---------------------------------------------------------
    # Hauptmethode: Element parsen
    # ---------------------------------------------------------
    def parse_element(self, raw_element):
        """
        raw_element: z.B. "KWH:3.5"
        Rückgabe: ["KWH", "3.5"]
        """

        if raw_element is None:
            return []

        raw_element = raw_element.strip()

        # Composite-Element?
        if self.component_separator in raw_element:
            return raw_element.split(self.component_separator)

        # Einfaches Element
        return [raw_element]

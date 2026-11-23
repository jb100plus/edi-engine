from .fsm_engine import FSMEngine
from .loader.registry_loader import RegistryLoader
from .loader.yaml_loader import YAMLLoader
from .parser.segment_parser import SegmentParser
from .parser.unh_parser import UNHParser


class EdifactEngine:
    """
    Universelle EDIFACT-Engine.
    Lädt Registry, FSM, Actions und Segmente und verarbeitet eine EDIFACT-Nachricht.
    """

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.registry_loader = RegistryLoader(base_path)
        self.yaml_loader = YAMLLoader()

        self.segment_parser = SegmentParser()
        self.unh_parser = UNHParser()

    # ---------------------------------------------------------
    # Hilfsfunktionen
    # ---------------------------------------------------------

    def _materialize(self, lines):
        """Sichert zu, dass lines mehrfach durchlaufen werden können."""
        return list(lines) if not isinstance(lines, list) else lines

    def _detect_message_type(self, lines):
        """Liest UNH und bestimmt den Nachrichtentyp."""
        for line in lines:
            line = line.strip()
            if line.startswith("UNH"):
                seg = self.segment_parser.parse_segment(line)
                return self.unh_parser.extract_message_type(seg)
        return None

    def _init_fsm(self, message_type):
        """Lädt Registry, FSM, Actions und Segmente."""
        entry = self.registry_loader.get_entry(message_type)

        fsm_yaml = self.yaml_loader.load_yaml(entry["fsm"])
        actions_class = entry["actions"]
        segments_yaml = self.yaml_loader.load_yaml(entry["segments"])

        context = {"segments_def": segments_yaml}
        actions = actions_class(context)
        fsm = FSMEngine(fsm_yaml, actions)

        return fsm, context

    # ---------------------------------------------------------
    # Hauptmethode
    # ---------------------------------------------------------

    def process_message(self, lines):
        """Verarbeitet eine EDIFACT-Nachricht vollständig."""
        lines = self._materialize(lines)

        # Nachrichtentyp bestimmen
        message_type = self._detect_message_type(lines)
        if not message_type:
            raise ValueError("UNH-Segment nicht gefunden – Nachrichtentyp unbekannt")

        # FSM initialisieren
        fsm, context = self._init_fsm(message_type)

        # Nachricht durchlaufen
        for raw in lines:
            raw = raw.strip()
            if not raw:
                continue

            segment = self.segment_parser.parse_segment(raw)
            fsm.handle_event(segment["tag"], segment)

            state = fsm.states.get(fsm.current_state, {})
            if state.get("terminal"):
                break

        # Dateiende übergeben, damit die FSM einen vorzeitigen Abschluss erkennt
        if not fsm.states.get(fsm.current_state, {}).get("terminal"):
            fsm.handle_event("EOF")

        return context.get("message")

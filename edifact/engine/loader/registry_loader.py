import yaml
from pathlib import Path
import importlib


class RegistryLoader:
    """
    Lädt registry.yaml und liefert den Eintrag für einen Nachrichtentyp.
    Wandelt Pfade in absolute Pfade um und lädt die Actions-Klasse dynamisch.
    """

    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.registry_file = self.base_path / "registry.yaml"

    # ---------------------------------------------------------
    # Registry laden
    # ---------------------------------------------------------
    def load_registry(self):
        with open(self.registry_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    # ---------------------------------------------------------
    # Eintrag für Nachrichtentyp holen
    # ---------------------------------------------------------
    def get_entry(self, message_type):
        registry = self.load_registry()

        if message_type not in registry:
            raise ValueError(f"Nachrichtentyp '{message_type}' nicht in registry.yaml gefunden")

        entry = registry[message_type]

        # Pfade absolut machen
        entry["fsm"] = str(self.base_path / "fsm" / entry["fsm"])
        entry["segments"] = str(self.base_path / "segments" / entry["segments"])

        # Actions-Klasse importieren
        entry["actions"] = self._import_actions(entry["actions"])

        return entry

    # ---------------------------------------------------------
    # Actions dynamisch importieren
    # ---------------------------------------------------------
    def _import_actions(self, dotted_path):
        """
        Erwartet z.B.:
        edifact.engine.actions.actions_mscons.MSCONS_Actions
        """
        module_name, class_name = dotted_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

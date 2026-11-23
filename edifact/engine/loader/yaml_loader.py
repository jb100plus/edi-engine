import yaml
from pathlib import Path
from yaml.loader import SafeLoader

# Alle impliziten Resolver entfernen
SafeLoader.yaml_implicit_resolvers = {}

class YAMLLoader:
    """
    Lädt YAML-Dateien (FSM, Segmente, Actions-Definitionen).
    """

    def load_yaml(self, path):
        """
        path: absoluter Pfad zu einer YAML-Datei
        Rückgabe: dict
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"YAML-Datei nicht gefunden: {path}")

        with open(path, "r", encoding="utf-8") as f:
            return yaml.load(f, Loader=SafeLoader)


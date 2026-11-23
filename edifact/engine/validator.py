class SegmentValidator:
    """Validiert Segmente anhand der geladenen Segment-Grammatik."""

    def __init__(self, segments_definition):
        self.definitions = segments_definition.get("segments", {})
        self.counts = {}

    def validate_segment(self, segment):
        tag = segment["tag"]
        definition = self.definitions.get(tag)

        if definition is None:
            return

        self.counts[tag] = self.counts.get(tag, 0) + 1

        max_repeat = int(definition.get("max_repeat", 1))
        if self.counts[tag] > max_repeat:
            raise ValueError(
                f"Segment '{tag}' überschreitet max_repeat={max_repeat}"
            )

        elements = segment.get("elements", [])
        element_specs = definition.get("elements", [])

        for index, element_spec in enumerate(element_specs, start=1):
            present = index <= len(elements)
            component_specs = element_spec.get("components", [])

            if self._is_true(element_spec.get("required")) and (not present or not elements[index - 1]):
                raise ValueError(
                    f"Pflicht-Datenelement {index} fehlt in Segment '{tag}'"
                )

            if not present:
                continue

            value = elements[index - 1]
            if isinstance(value, list):
                single_value = ":".join(value)
            else:
                single_value = str(value)

            min_length = element_spec.get("min_length")
            max_length = element_spec.get("max_length")
            min_length = int(min_length) if min_length is not None else None
            max_length = int(max_length) if max_length is not None else None

            if min_length is not None and len(single_value) < min_length:
                raise ValueError(f"Datenelement {index} in Segment '{tag}' ist zu kurz")
            if max_length is not None and len(single_value) > max_length:
                raise ValueError(f"Datenelement {index} in Segment '{tag}' ist zu lang")

            components = elements[index - 1]
            for component_index, component_spec in enumerate(component_specs, start=1):
                component_present = (
                    component_index <= len(components)
                    and components[component_index - 1] != ""
                )

                if self._is_true(component_spec.get("required")) and not component_present:
                    raise ValueError(
                        f"Pflicht-Komponente {component_index} fehlt in Datenelement "
                        f"{index} von Segment '{tag}'"
                    )

                if component_present:
                    value = components[component_index - 1]
                    min_length = component_spec.get("min_length")
                    max_length = component_spec.get("max_length")
                    min_length = int(min_length) if min_length is not None else None
                    max_length = int(max_length) if max_length is not None else None

                    if min_length is not None and len(value) < min_length:
                        raise ValueError(
                            f"Komponente {component_index} in Segment '{tag}' ist zu kurz"
                        )
                    if max_length is not None and len(value) > max_length:
                        raise ValueError(
                            f"Komponente {component_index} in Segment '{tag}' ist zu lang"
                        )

    def validate_required_segments(self):
        for tag, definition in self.definitions.items():
            if not self._is_true(definition.get("required")):
                continue

            count = self.counts.get(tag, 0)
            min_repeat = int(definition.get("min_repeat", 1))

            if count < min_repeat:
                raise ValueError(
                    f"Pflichtsegment '{tag}' fehlt oder wurde zu selten wiederholt"
                )

    @staticmethod
    def _is_true(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"true", "yes", "1"}
        return bool(value)

from edifact.engine.validator import SegmentValidator


class GenericActions:
    """Grammar-driven actions without knowledge of EDIFACT message types."""

    def __init__(self, context):
        self.ctx = context
        self.validator = SegmentValidator(context.get("segments_def", {}))

    def init_message(self, segment=None, element=None):
        self.ctx["message"] = {
            "header": {},
            "body": [],
            "trailer": {},
        }

    def store_segment(self, segment, element=None):
        if segment is None:
            return

        self.validator.validate_segment(segment)

        tag = segment["tag"]
        segments_def = self.ctx.get("segments_def", {}).get("segments", {})
        definition = segments_def.get(tag, {})
        role = definition.get("role", "body")
        max_repeat = int(definition.get("max_repeat", 1))
        multiple = max_repeat > 1 or bool(definition.get("multiple", False))

        if role == "header":
            target = self.ctx["message"]["header"]
        elif role == "trailer":
            target = self.ctx["message"]["trailer"]
        else:
            self.ctx["message"]["body"].append(segment)
            return

        if multiple:
            target.setdefault(tag, []).append(segment)
        else:
            target[tag] = segment

    def finalize_message(self, segment=None, element=None):
        self.validator.validate_required_segments()

    def handle_unexpected_segment(self, segment, element=None):
        raise ValueError(f"Unexpected segment encountered: {segment}")

    def handle_premature_end(self, segment=None, element=None):
        raise ValueError("Message ended before UNT")

class FSMEngine:
    """
    Universelle FSM-Engine für EDIFACT.
    Lädt eine FSM aus YAML und führt Events + Actions aus.
    """

    def __init__(self, fsm_definition, actions):
        self.states = fsm_definition.get("states", {})
        self.errors = fsm_definition.get("errors", {})
        self.actions = actions
        self.current_state = "START"

        print("FSM STATES:", list(self.states.keys()))

    # ---------------------------------------------------------
    # Event-Verarbeitung
    # ---------------------------------------------------------
    def handle_event(self, event_type, segment=None, element=None):
        print("FSM EVENT:", event_type, "STATE:", self.current_state)

        state_def = self.states.get(self.current_state, {})
        transitions = state_def.get("on", {})

        # 1. Direkter Match?
        if event_type not in transitions:

            # 2. Wildcard SEGMENT?
            if "SEGMENT" in transitions:
                event_type = "SEGMENT"
            else:
                return self._handle_error("unexpected_segment", segment, element)

        # 3. Transition ausführen
        transition = transitions[event_type]
        target = transition.get("target")
        actions = transition.get("actions", [])

        for action_name in actions:
            self._run_action(action_name, segment, element)

        # 4. Zustand wechseln
        self.current_state = target

        # 5. Terminalzustand prüfen (NEUER Zustand!)
        if self.states.get(self.current_state, {}).get("terminal"):
            return

    # ---------------------------------------------------------
    # Action Dispatcher
    # ---------------------------------------------------------
    def _run_action(self, action_name, segment, element):
        if not hasattr(self.actions, action_name):
            raise ValueError(f"Action '{action_name}' nicht implementiert")

        method = getattr(self.actions, action_name)
        method(segment, element)

    # ---------------------------------------------------------
    # Fehlerbehandlung
    # ---------------------------------------------------------
    def _handle_error(self, error_key, segment, element):
        if error_key not in self.errors:
            raise ValueError(f"Unbekannter Fehler: {error_key}")

        error_def = self.errors[error_key]
        action_name = error_def.get("action")

        if hasattr(self.actions, action_name):
            getattr(self.actions, action_name)(segment, element)

        msg = error_def.get("message", "Unbekannter Fehler")
        raise ValueError(msg)

    def reset(self):
        self.current_state = "START"

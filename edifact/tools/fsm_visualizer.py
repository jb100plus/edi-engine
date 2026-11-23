import os
import yaml

def load_fsm(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def generate_dot(fsm):
    states = fsm["states"]

    dot = []
    dot.append('digraph FSM {')
    dot.append('  rankdir=LR;')
    dot.append('  node [shape=box, style=filled, fontname="Arial"];')

    # States
    for state in states:
        if state == "END":
            dot.append(f'  {state} [shape=doublecircle, fillcolor="#C6EFCE"];')
        elif state == "START":
            dot.append(f'  {state} [fillcolor="#FFF2CC"];')
        else:
            dot.append(f'  {state} [fillcolor="#D9E1F2"];')

    # Transitions
    for state, defn in states.items():
        if "on" not in defn:
            continue
        for event, trans in defn["on"].items():
            target = trans["target"]
            dot.append(f'  {state} -> {target} [label="{event}"];')

    dot.append("}")
    return "\n".join(dot)

def find_file(filename, start_dir):
    for root, dirs, files in os.walk(start_dir):
        if filename in files:
            return os.path.join(root, filename)
    return None

if __name__ == "__main__":
    BASE = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))

    FSM_PATH = os.path.join( "/home/juergen/Projekte/edi-engine/edifact/grammars/fsm", "fsm_mscons.yaml")
    fsm = load_fsm(FSM_PATH)
    if not FSM_PATH:
        raise FileNotFoundError("fsm_mscons.yaml nicht gefunden!")

    fsm = load_fsm(FSM_PATH)
    dot = generate_dot(fsm)

    out_path = os.path.join(BASE, "fsm_mscons_auto.dot")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(dot)

    print("FSM Visualisierung erzeugt:", out_path)



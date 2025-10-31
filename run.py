from devteam.langgraphs.master_graph import *
from rich.console import Console
import asyncio
from langgraph.pregel.main import PregelRunner
import joblib
import os

def resume_graph(create_graph_func, checkpoint_path="devteam_checkpoint.pkl", **kwargs):
    """Resume from checkpoint if available; otherwise start from scratch."""
    if not os.path.exists(checkpoint_path):
        print("🚀 No checkpoint found. Starting fresh...")
        g = create_graph_func(**kwargs)
        app = g.compile()
        return asyncio.run(app.ainvoke({}))

    print("🔄 Found checkpoint, attempting to resume...")
    ckpt = joblib.load(checkpoint_path)
    state, last_node = ckpt["state"], ckpt["last_node"]
    print(f"✅ Checkpoint resume: last_node = '{last_node}'")

    g = create_graph_func(**kwargs)
    app = g.compile()

    node_container = None
    for attr in ("graph", "state_graph", "nodes"):
        if hasattr(app, attr):
            candidate = getattr(app, attr)
            if hasattr(candidate, "nodes"):
                node_container = candidate.nodes
            elif isinstance(candidate, dict):
                node_container = candidate
            if node_container is not None:
                break
    if node_container is None:
        raise RuntimeError("Could not locate node container on compiled graph.")

    all_nodes = [
        "UserInput",
        "ProjectOverview",
        "FileListing",
        "Responsibilities",
        "Dependencies",
        "Classes",
        "JSFunctions",
        "Architecture",
        "Implementation",
    ]
    start_index = all_nodes.index(last_node) + 1
    next_nodes = all_nodes[start_index:]

    if not next_nodes:
        print("✅ All nodes already completed.")
        return state

    print(f"➡️  Resuming at node '{next_nodes[0]}' (skipping {start_index} completed nodes)\n")

    async def run_remaining_nodes(state):
        for node_name in next_nodes:
            node_spec = node_container[node_name]

            if not hasattr(node_spec, "ainvoke"):
                raise RuntimeError(f"Node '{node_name}' has no 'ainvoke' method — unsupported type {type(node_spec)}")

            print(f"▶️  Executing node: {node_name}")
            state = await node_spec.ainvoke(state)
            joblib.dump({"state": state, "last_node": node_name}, checkpoint_path)
        return state

    return asyncio.run(run_remaining_nodes(state))




if __name__ == "__main__":
    console = Console()
    final_state = resume_graph(create_master_graph, console=console)
    
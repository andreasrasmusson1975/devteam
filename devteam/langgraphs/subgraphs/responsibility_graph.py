from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from devteam.generation.architecture.responsibilities_generation.responsibilities import *
from devteam.helper_functionality.helpers import *
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class ResponsibilityState(BaseModel):
    system_prompt: str
    project_overview:Dict[str, Any]
    files_listing: Optional[Dict[str, Any]] = None
    file_name: str
    responsibilities: Dict[str, List[str]] = {}
    message: Optional[str] = None
    conversation: Optional[list] = []

async def generate_responsibilities(state):
    user_prompt = get_responsibilities_user_prompt(
        project_overview=json.dumps(state.project_overview),
        files_listing=json.dumps(state.files_listing),
        file_name=state.file_name,

    )
    responsibilities = await get_responsibilities(
        user_prompt,
        state.system_prompt
    )
    state.responsibilities = responsibilities
    state.files_listing = add_responsibilities(state.files_listing, state.file_name, responsibilities)
    return state

graph = StateGraph(
    state_schema = ResponsibilityState
)
graph.add_node("generate_responsibilities", generate_responsibilities)
graph.set_entry_point("generate_responsibilities")
graph.add_edge("generate_responsibilities", END)

async def run_responsibility_graph(
    system_prompt: str,
    project_overview: Dict[str, Any],
    files_listing: Dict[str, Any],
    file_name: str,
) -> ResponsibilityState:
    compiled = graph.compile()
    initial_state = ResponsibilityState(
        system_prompt=system_prompt,
        project_overview=project_overview,
        files_listing=files_listing,
        file_name=file_name,
    )
    final_state = await compiled.ainvoke(initial_state)
    return final_state

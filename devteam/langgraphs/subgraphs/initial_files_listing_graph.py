from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from devteam.generation.architecture.file_listing_generation.file_listing import *
from devteam.helper_functionality.helpers import *
from typing import Optional, Dict, Any
from pydantic import BaseModel

class InitialFilesListingState(BaseModel):
    user_prompt: list
    system_prompt: str
    project_overview:Dict[str, Any]
    files_listing: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    conversation: Optional[list] = []

async def generate_initial_files_listing(state):
    user_prompt = get_initial_file_listing_user_prompt(
        json.dumps(state.project_overview),
        get_files_listing_input_schema()
    )
    files_listing = await get_initial_files_listing(
        user_prompt,
    )
    state.files_listing = files_listing
    return state

graph = StateGraph(
    state_schema = InitialFilesListingState
)
graph.add_node("generate_initial_files_listing", generate_initial_files_listing)
graph.set_entry_point("generate_initial_files_listing")
graph.add_edge("generate_initial_files_listing", END)

async def run_initial_files_listing_graph(
    user_prompt: list,
    system_prompt: str,
    project_overview: Dict[str, Any],
) -> InitialFilesListingState:
    compiled = graph.compile()
    initial_state = InitialFilesListingState(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        project_overview=project_overview,
    )
    final_state = await compiled.ainvoke(initial_state)
    return final_state
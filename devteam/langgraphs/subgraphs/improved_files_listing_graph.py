from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from devteam.generation.architecture.file_listing_generation.file_listing import *
from devteam.helper_functionality.helpers import *
from typing import Optional, Dict, Any
from pydantic import BaseModel

class ImprovedFilesListingState(BaseModel):
    original_user_prompt: str
    system_prompt: str
    project_overview:Dict[str, Any]
    files_listing: Dict[str, Any]
    message: Optional[str] = None
    changes_made: Optional[list] = []
    conversation: Optional[list] = []

async def generate_improved_files_listing(state):
    user_prompt = get_improved_file_listing_user_prompt(
        state.original_user_prompt,
        json.dumps(state.project_overview),
        json.dumps(state.files_listing),
        get_improved_files_listing_input_schema()
    )
    files_listing = await get_improved_files_listing(
        user_prompt
    )
    state.files_listing = files_listing
    state.changes_made = files_listing.get("changes_made")
    return state

graph = StateGraph(
    state_schema = ImprovedFilesListingState
)
graph.add_node("generate_improved_files_listing", generate_improved_files_listing)
graph.set_entry_point("generate_improved_files_listing")
graph.add_edge("generate_improved_files_listing", END)

async def run_improved_files_listing_graph(
    original_user_prompt: str,
    system_prompt: str,
    project_overview: Dict[str, Any],
    files_listing: Dict[str, Any],
) -> ImprovedFilesListingState:
    compiled = graph.compile()
    initial_state = ImprovedFilesListingState(
        original_user_prompt=original_user_prompt,
        system_prompt=system_prompt,
        project_overview=project_overview,
        files_listing=files_listing,
    )
    final_state = await compiled.ainvoke(initial_state)
    return final_state
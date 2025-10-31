from langgraph.graph import StateGraph, END
from devteam.generation.architecture.class_generation.class_generation import *
from devteam.helper_functionality.helpers import *
from typing import Optional, Dict, Any
from pydantic import BaseModel

class ClassGenerationState(BaseModel):
    original_user_prompt: str
    system_prompt: str
    project_overview:Dict[str, Any]
    files_listing: Dict[str, Any]
    file_name: str
    class_dict: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    conversation: Optional[list] = []
    
    

async def generate_initial_class(state):
    user_prompt = get_class_generation_user_prompt(
        state.original_user_prompt,
        json.dumps(state.project_overview),
        json.dumps(state.files_listing),
        state.file_name,
        get_class_generation_input_schema()
    )
    class_dict = await get_class(
        user_prompt,
        state.system_prompt
    )
    state.class_dict = class_dict
    return state

graph = StateGraph(
    state_schema = ClassGenerationState
)
graph.add_node("generate_initial_class", generate_initial_class)
graph.set_entry_point("generate_initial_class")
graph.add_edge("generate_initial_class", END)

async def run_initial_class_generation_graph(
    original_user_prompt: str,
    system_prompt: str,
    project_overview: Dict[str, Any],
    files_listing: Dict[str, Any],
    file_name: str,
) -> ClassGenerationState:
    compiled = graph.compile()
    initial_state = ClassGenerationState(
        original_user_prompt=original_user_prompt,
        system_prompt=system_prompt,
        project_overview=project_overview,
        files_listing=files_listing,
        file_name=file_name,
    )
    final_state = await compiled.ainvoke(initial_state)
    return final_state
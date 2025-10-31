from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from devteam.generation.architecture.js_function_generation.js_function_generation import *
from devteam.helper_functionality.helpers import *
from typing import Optional, Dict, Any
from pydantic import BaseModel

class JSFunctionGenerationState(BaseModel):
    original_user_prompt: str
    system_prompt: str
    project_overview: Dict[str, Any]
    files_listing: Dict[str, Any]
    file_name: str
    function_dict: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    conversation: Optional[list] = []

async def generate_js_function(state):
    user_prompt = get_js_function_generation_user_prompt(
        state.original_user_prompt,
        json.dumps(state.project_overview),
        json.dumps(state.files_listing),
        state.file_name,
        get_js_function_generation_input_schema()
    )
    function_dict = await get_js_function(
        user_prompt,
        state.system_prompt
    )
    state.function_dict = function_dict
    return state

graph = StateGraph(
    state_schema = JSFunctionGenerationState
)
graph.add_node("generate_js_function", generate_js_function)
graph.set_entry_point("generate_js_function")
graph.add_edge("generate_js_function", END)

async def run_js_function_generation_graph(
    original_user_prompt: str,
    system_prompt: str,
    project_overview: Dict[str, Any],
    files_listing: Dict[str, Any],
    file_name: str,
) -> JSFunctionGenerationState:
    compiled = graph.compile()
    initial_state = JSFunctionGenerationState(
        original_user_prompt=original_user_prompt,
        system_prompt=system_prompt,
        project_overview=project_overview,
        files_listing=files_listing,
        file_name=file_name,
    )
    final_state = await compiled.ainvoke(initial_state)
    return final_state

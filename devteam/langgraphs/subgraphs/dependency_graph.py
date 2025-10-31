from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from devteam.generation.architecture.dependency_generation.dependencies import *
from devteam.helper_functionality.helpers import *
from typing import Optional, Dict, Any
from pydantic import BaseModel

class DependencyGraphState(BaseModel):
    files_listing: Dict[str, Any]
    partial_dependency_list: list
    file_name: str
    system_prompt: str
    dependencies_dict: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    conversation: Optional[list] = []

async def generate_dependencies(state):
    user_prompt = get_dependencies_user_prompt(
        files_listing=state.files_listing,
        partial_dependency_list=state.partial_dependency_list,
        file_name=state.file_name,
        schema=get_dependencies_input_schema()
    )
    response = await get_dependencies(
        user_prompt=user_prompt,
        system_prompt=state.system_prompt
    )
    state.dependencies_dict = response
    return state

graph = StateGraph(
    state_schema=DependencyGraphState
)
graph.add_node("generate_dependencies", generate_dependencies)
graph.set_entry_point("generate_dependencies")
graph.add_edge("generate_dependencies", END)

async def run_dependency_graph(
    files_listing: Dict[str, Any],
    partial_dependency_list: list,
    file_name: str,
    system_prompt: str,
) -> DependencyGraphState:
    compiled = graph.compile()
    initial_state = DependencyGraphState(
        files_listing=files_listing,
        partial_dependency_list=partial_dependency_list,
        file_name=file_name,
        system_prompt=system_prompt,
    )
    final_state = await compiled.ainvoke(initial_state)
    return final_state

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from devteam.generation.file_content.pyproject_toml_file_content_generation.pyproject_toml_files import *
from devteam.helper_functionality.helpers import *
from typing import Optional, Dict, Any
from pydantic import BaseModel

class PyprojectTomlFileState(BaseModel):
    architecture_dict: Dict[str, Any]
    implementations_so_far: list
    file_name: str
    system_prompt: str
    pyproject_toml_file_content: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    conversation: Optional[list] = []

async def generate_pyproject_toml_file_content(state):
    user_prompt = get_pyproject_toml_user_prompt(
        architecture_dict=state.architecture_dict,
        implementations_so_far=state.implementations_so_far,
        file_name=state.file_name,
    )
    pyproject_toml_file_content = await get_pyproject_toml_file_content(
        user_prompt,
        state.system_prompt
    )
    state.pyproject_toml_file_content = pyproject_toml_file_content
    return state

graph = StateGraph(
    state_schema = PyprojectTomlFileState
)

graph.add_node("generate_pyproject_toml_file_content", generate_pyproject_toml_file_content)
graph.set_entry_point("generate_pyproject_toml_file_content")
graph.add_edge("generate_pyproject_toml_file_content", END)

async def run_pyproject_toml_file_generation_graph(
    architecture_dict: Dict[str, Any],
    implementations_so_far: list,
    file_name: str,
    system_prompt: str,
) -> PyprojectTomlFileState:
    compiled = graph.compile()
    initial_state = PyprojectTomlFileState(
        architecture_dict=architecture_dict,
        implementations_so_far=implementations_so_far,
        file_name=file_name,
        system_prompt=system_prompt,
    )
    final_state = await compiled.ainvoke(initial_state)
    return final_state
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from devteam.generation.file_content.install_file_generation.install_files import *
from devteam.helper_functionality.helpers import *
from typing import Optional, Dict, Any
from pydantic import BaseModel

class InstallFileState(BaseModel):
    architecture_dict: Dict[str, Any]
    implementations_so_far: list
    file_name: str
    system_prompt: str
    install_file_content: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    conversation: Optional[list] = []

async def generate_install_file_content(state):
    user_prompt = get_install_file_user_prompt(
        architecture_dict=state.architecture_dict,
        implementations_so_far=state.implementations_so_far,
        file_name=state.file_name,
    )
    install_file_content = await get_install_file_content(
        user_prompt,
        state.system_prompt
    )
    state.install_file_content = install_file_content
    return state

graph = StateGraph(
    state_schema = InstallFileState
)

graph.add_node("generate_install_file_content", generate_install_file_content)
graph.set_entry_point("generate_install_file_content")
graph.add_edge("generate_install_file_content", END)

async def run_install_file_generation_graph(
    architecture_dict: Dict[str, Any],
    implementations_so_far: list,
    file_name: str,
    system_prompt: str,
) -> InstallFileState:
    compiled = graph.compile()
    initial_state = InstallFileState(
        architecture_dict=architecture_dict,
        implementations_so_far=implementations_so_far,
        file_name=file_name,
        system_prompt=system_prompt,
    )
    final_state = await compiled.ainvoke(initial_state)
    return final_state
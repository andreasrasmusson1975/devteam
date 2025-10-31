from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from devteam.generation.file_content.css_file_content_generation.css_files import *
from devteam.helper_functionality.helpers import *
from typing import Optional, Dict, Any
from pydantic import BaseModel

class CssFileState(BaseModel):
    architecture_dict: Dict[str, Any]
    implementations_so_far: list
    file_name: str
    system_prompt: str
    css_file_content: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    conversation: Optional[list] = []

async def generate_css_file_content(state):
    user_prompt = get_css_file_user_prompt(
        architecture_dict=state.architecture_dict,
        implementations_so_far=state.implementations_so_far,
        file_name=state.file_name,
    )
    css_file_content = await get_css_file_content(
        user_prompt,
        state.system_prompt
    )
    state.css_file_content = css_file_content
    return state

graph = StateGraph(
    state_schema = CssFileState
)
graph.add_node("generate_css_file_content", generate_css_file_content)
graph.set_entry_point("generate_css_file_content")
graph.add_edge("generate_css_file_content", END)

async def run_css_file_generation_graph(
    architecture_dict: Dict[str, Any],
    implementations_so_far: list,
    file_name: str,
    system_prompt: str,
) -> CssFileState:
    compiled = graph.compile()
    initial_state = CssFileState(
        architecture_dict=architecture_dict,
        implementations_so_far=implementations_so_far,
        file_name=file_name,
        system_prompt=system_prompt,
    )
    final_state = await compiled.ainvoke(initial_state)
    return final_state

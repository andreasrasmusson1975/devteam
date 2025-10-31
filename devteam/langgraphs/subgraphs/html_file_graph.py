from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from devteam.generation.file_content.html_file_content_generation.html_files import *
from devteam.helper_functionality.helpers import *
from typing import Optional, Dict, Any
from pydantic import BaseModel

class HtmlFileState(BaseModel):
    architecture_dict: Dict[str, Any]
    implementations_so_far: list
    file_name: str
    system_prompt: str
    html_file_content: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    conversation: Optional[list] = []

async def generate_html_file_content(state):
    user_prompt = get_html_file_user_prompt(
        architecture_dict=state.architecture_dict,
        implementations_so_far=state.implementations_so_far,
        file_name=state.file_name,
    )
    html_file_content = await get_html_file_content(
        user_prompt,
        state.system_prompt
    )
    state.html_file_content = html_file_content
    return state

graph = StateGraph(
    state_schema = HtmlFileState
)
graph.add_node("generate_html_file_content", generate_html_file_content)
graph.set_entry_point("generate_html_file_content")
graph.add_edge("generate_html_file_content", END)

async def run_html_file_generation_graph(
    architecture_dict: Dict[str, Any],
    implementations_so_far: list,
    file_name: str,
    system_prompt: str,
) -> HtmlFileState:
    compiled = graph.compile()
    initial_state = HtmlFileState(
        architecture_dict=architecture_dict,
        implementations_so_far=implementations_so_far,
        file_name=file_name,
        system_prompt=system_prompt,
    )
    final_state = await compiled.ainvoke(initial_state)
    return final_state
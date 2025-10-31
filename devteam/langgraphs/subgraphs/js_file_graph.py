from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from devteam.generation.file_content.js_file_content_generation.js_files import *
from devteam.helper_functionality.helpers import *
from typing import Optional, Dict, Any
from pydantic import BaseModel

class JsFileState(BaseModel):
    architecture_dict: Dict[str, Any]
    implementations_so_far: list
    file_name: str
    system_prompt: str
    js_file_content: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    conversation: Optional[list] = []

async def generate_js_file_content(state):
    user_prompt = get_js_file_user_prompt(
        architecture_dict=state.architecture_dict,
        implementations_so_far=state.implementations_so_far,
        file_name=state.file_name,
    )
    js_file_content = await get_js_file_content(
        user_prompt,
        state.system_prompt
    )
    state.js_file_content = js_file_content
    return state

graph = StateGraph(
    state_schema = JsFileState
)
graph.add_node("generate_js_file_content", generate_js_file_content)
graph.set_entry_point("generate_js_file_content")
graph.add_edge("generate_js_file_content", END)

async def run_js_file_generation_graph(
    architecture_dict: Dict[str, Any],
    implementations_so_far: list,
    file_name: str,
    system_prompt: str,
) -> JsFileState:
    compiled = graph.compile()
    initial_state = JsFileState(
        architecture_dict=architecture_dict,
        implementations_so_far=implementations_so_far,
        file_name=file_name,
        system_prompt=system_prompt,
    )
    final_state = await compiled.ainvoke(initial_state)
    return final_state
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from devteam.generation.file_content.env_file_content_generation.env_file import *
from devteam.helper_functionality.helpers import *
from typing import Optional, Dict, Any
from pydantic import BaseModel

class EnvFileState(BaseModel):
    architecture_dict: Dict[str, Any]
    file_name: str
    system_prompt: str
    env_file_content: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    conversation: Optional[list] = []

async def generate_env_file_content(state):
    user_prompt = get_env_file_user_prompt(
        state.architecture_dict,
        state.file_name
    )
    env_file_content = await get_env_file_content(
        user_prompt,
        state.system_prompt
    )
    content = parse_env_file_content(env_file_content)
    state.env_file_content = {"file_name": state.file_name, "content": content}
    return state

graph = StateGraph(
    state_schema = EnvFileState
)
graph.add_node("generate_env_file_content", generate_env_file_content)
graph.set_entry_point("generate_env_file_content")
graph.add_edge("generate_env_file_content", END)

async def run_env_file_generation_graph(
    architecture_dict: Dict[str, Any],
    file_name: str,
    system_prompt: str,
) -> EnvFileState:
    compiled = graph.compile()
    initial_state = EnvFileState(
        architecture_dict=architecture_dict,
        file_name=file_name,
        system_prompt=system_prompt,
    )
    final_state = await compiled.ainvoke(initial_state)
    return final_state

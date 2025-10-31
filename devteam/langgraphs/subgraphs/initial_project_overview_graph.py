from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from devteam.generation.architecture.project_overview_generation.project_overview import *
from devteam.helper_functionality.helpers import *
from typing import Optional, Dict, Any
from pydantic import BaseModel

class InitialProjectOverviewState(BaseModel):
    user_prompt: str
    system_prompt: str
    classification: Optional[Dict[str, Any]] = None
    project_overview: Optional[Dict[str, Any]] = None
    classify: bool = True
    message: Optional[str] = None
    conversation: Optional[list] = []

async def classify_initial_input(state):
    if state.classify:
        user_prompt = state.user_prompt
        user_prompt = get_initial_user_prompt([], user_prompt, get_user_prompt_input_schema())
        classification = await get_user_prompt_classification(
            user_prompt,
            state.system_prompt,
        )
        state.classification = classification
    else:
        state.classification = {
            "category": 0,
            "confidence": 1.0,
            "explanation": "Skipping classification as per user request.",
            "warnings_about_content": []
        }
    return state

async def handle_bad_initial_content(state):
    state.message = bad_content_detected_init
    return state

async def handle_confusing_initial_content(state):
    state.message = confusing_initial_content_detected_init
    return state

async def generate_initial_project_overview(state):
    if not state.classify:
        user_prompt = state.user_prompt
        user_prompt = get_initial_user_prompt([], user_prompt, get_user_prompt_input_schema())
        project_overview, lines = await get_initial_project_overview(
            user_prompt,
        )
        state.project_overview = project_overview
        state.message = "\n".join(lines)
    return state

graph = StateGraph(
    state_schema = InitialProjectOverviewState
)
graph.add_node("classify_input", classify_initial_input)
graph.add_node("handle_bad_initial_content", handle_bad_initial_content)
graph.add_node("handle_confusing_initial_content", handle_confusing_initial_content)
graph.add_node("generate_initial_project_overview", generate_initial_project_overview)

graph.set_entry_point("classify_input")

graph.add_conditional_edges(
    "classify_input",
    lambda state: state.classification["category"],
    {
        0: "generate_initial_project_overview",
        1: "handle_bad_initial_content",
        2: "handle_confusing_initial_content",
    }
)

async def run_initial_project_overview(user_prompt,classify: bool = True) -> InitialProjectOverviewState:
    compiled = graph.compile()
    state = InitialProjectOverviewState(
        user_prompt=user_prompt,
        system_prompt=IPOC,
        classification={
            "category": -1,
            "confidence": 0.0,
            "explanation": "",
            "warnings_about_content": []
        },
        project_overview=None,
        classify=classify,
        message=None,
        conversation=[],
    )
    final_state = await compiled.ainvoke(state)
    return final_state






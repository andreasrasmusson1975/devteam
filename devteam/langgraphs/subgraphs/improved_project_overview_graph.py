from devteam.langgraphs.subgraphs.initial_project_overview_graph import InitialProjectOverviewState
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from devteam.generation.architecture.project_overview_generation.project_overview import *
from devteam.helper_functionality.helpers import *
from typing import Optional, Dict, Any
from pydantic import BaseModel

class ImprovedProjectOverviewState(BaseModel):
    user_prompt: str
    system_prompt: str
    classification: Optional[Dict[str, Any]] = None
    project_overview: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    conversation: Optional[list] = []

async def classify_improvement_input(state):
    user_prompt = state.user_prompt
    user_prompt = get_initial_user_prompt([], user_prompt, get_user_prompt_input_schema())
    classification = await get_user_prompt_classification(
        user_prompt,
        state.system_prompt,
    )
    state.classification = classification
    return state

async def handle_non_allowed_change(state):
    state.message = change_not_allowed
    return state

async def handle_bad_improvement_content(state):
    state.message = bad_content_detected_init
    return state

async def handle_confusing_improvement_content(state):
    state.message = confusing_project_overview_improvement_content_detected_init
    return state

async def generate_improved_project_overview(state):
    user_prompt = state.user_prompt
    user_prompt = get_project_overview_improvement_user_prompt(
        json.dumps(state.project_overview), 
        user_prompt, 
        get_project_overview_improvement_input_schema()
    )
    project_overview, lines = await get_improved_project_overview(user_prompt)
    state.project_overview = project_overview
    state.message = "\n".join(lines)
    return state

async def handle_accepted_project_overview(state):
    state.message = accepted_project_overview_init
    return state

graph = StateGraph(
    state_schema = ImprovedProjectOverviewState
)
graph.add_node("classify_input", classify_improvement_input)
graph.add_node("handle_non_allowed_change", handle_non_allowed_change)
graph.add_node("handle_bad_improvement_content", handle_bad_improvement_content)
graph.add_node("handle_confusing_improvement_content", handle_confusing_improvement_content)
graph.add_node("handle_accepted_project_overview", handle_accepted_project_overview)
graph.add_node("generate_improved_project_overview", generate_improved_project_overview)

graph.set_entry_point("classify_input")

graph.add_conditional_edges(
    "classify_input",
    lambda state: state.classification["category"],
    {
        0: "generate_improved_project_overview",
        1: "handle_non_allowed_change",
        2: "handle_accepted_project_overview",
        3: "handle_bad_improvement_content",
        4: "handle_confusing_improvement_content",
    }
)

async def run_improved_project_overview(project_overview: dict,user_prompt: str):
    compiled = graph.compile()
    state = InitialProjectOverviewState(
        user_prompt=user_prompt,
        system_prompt=IPOC2,
        classification={
            "category": -1,
            "confidence": 0.0,
            "explanation": "",
            "warnings_about_content": []
        },
        project_overview=project_overview,
        message=None,
        conversation=[],
    )
    final_state = await compiled.ainvoke(state)
    return final_state






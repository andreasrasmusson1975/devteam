from langgraph.graph import StateGraph, END
from devteam.langgraphs.subgraphs.initial_files_listing_graph import *
from devteam.generation.architecture.project_overview_generation.project_overview import *
from devteam.generation.architecture.file_listing_generation.file_listing import *
from devteam.langgraphs.subgraphs.initial_project_overview_graph import *
from devteam.langgraphs.subgraphs.improved_project_overview_graph import *
from devteam.langgraphs.subgraphs.improved_files_listing_graph import *
from devteam.langgraphs.subgraphs.class_graph import *
from devteam.langgraphs.subgraphs.responsibility_graph import *
from devteam.langgraphs.subgraphs.js_function_graph import *
from devteam.langgraphs.subgraphs.env_file_graph import *
from devteam.langgraphs.subgraphs.dependency_graph import *
from devteam.langgraphs.subgraphs.py_file_graph import *
from devteam.langgraphs.subgraphs.js_file_graph import *
from devteam.langgraphs.subgraphs.css_file_graph import *
from devteam.langgraphs.subgraphs.md_file_graph import *
from devteam.langgraphs.subgraphs.html_file_graph import *
from devteam.langgraphs.subgraphs.docker_file_graph import *
from devteam.langgraphs.subgraphs.install_file_graph import *
from devteam.langgraphs.subgraphs.pyproject_toml_file_graph import *
from devteam.system_prompts.system_prompts import *
from devteam.schemas.schema_creation import *
from devteam.helper_functionality.helpers import *
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import TextArea
from devteam.helper_functionality.helpers import *
from devteam.generation.architecture.file_structure_generation.file_structure import *
import joblib, asyncio
import sys, io, os
from typing import TypedDict

welcome = """
Hi! I'm here to help you realize your python project.
What would you like to build today?
If you need some inspiration, here are some ideas:
                           
"[italic]I want to build a web scraper that collects data from https://example.com and stores it in a database.[/italic]"

"[italic]I want to create a personal blog using sqlite as the database and Flask as the web framework.[/italic]"

"[italic]I want to build a chess game application with AI opponent. Use some open source chess engine for the AI. The GUI should be web-based.[/italic]"

"[italic]I want to develop a machine learning model to predict house prices based on various features. Use the california housing dataset.[/italic]"

"[italic]I want to create a RESTful API using Flask and SQLAlchemy.[/italic]"
"""

start_project = """
Certainly! I will forward your request to the architect who will create a project
overview. Once done, I will present it to you for review and approval.
"""

accepted = """
Perfect! I will now ask the architect to create the full architecture for the project.
I'll get back to you when it's done.
"""

console = Console()

def architecture_finished_message(architecture_dict):
    file_structure = create_file_structure(architecture_dict)
    markdown = generate_architecture_markdown(architecture_dict)
    save_architecture_to_file(markdown,architecture_dict)
    project_name = architecture_dict["project_overview"]["project_name"].lower().replace(" ", "_")
    save_path = Path().cwd() / project_name / "docs" / "architecture.pdf"
    architecture_finished = f"""
    The architecture for your project is complete. Moreover, the file structure 
    for the whole project has been created. The architecture has been saved to:
    
    {save_path} 
    
    Please review it and in the mean time, I will ask the coder to start filling 
    the other files with content.
    """
    console.print("")
    console.print("")
    console.print("🤵 [bold yellow]Project Manager:[/bold yellow]")
    console.print(Panel.fit(architecture_finished, border_style="cyan"))
    console.print("")
    return architecture_finished, file_structure

def render_user_input():
    for i in range(1):
        console.print("")
    user_input= input("🦹‍♀️ You: ")
    for _ in range(3):
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")
    sys.stdout.flush()
    console.print("🦹‍♀️ [bold cyan]You:[/bold cyan]")
    panel = Panel.fit(user_input, border_style="green")
    console.print(panel)
    console.print("")
    return user_input

async def conversation_start(state) -> str:
    console.print("")
    console.print("🤵 [bold yellow]Project Manager:[/bold yellow]")
    console.print(Panel.fit(welcome, border_style="cyan"))
    console.print("")
    console.print("")
    user_input = render_user_input()
    temp_state = await run_initial_project_overview(user_input,True)
    while temp_state["classification"]["category"] != 0:
        console.print("🤵 [bold yellow]Project Manager:[/bold yellow]")
        console.print(Panel.fit(temp_state["message"], border_style="cyan"))
        console.print("")
        user_input = render_user_input()
        temp_state = await run_initial_project_overview(user_input,True)
    console.print("🤵 [bold yellow]Project Manager:[/bold yellow]")
    console.print(Panel.fit(start_project, border_style="cyan"))
    console.print("")
    console.print(Markdown("👩‍🏭 Architect working on project overview..."))
    tempstate = await run_initial_project_overview(user_input,False)
    state["project_overview"] = tempstate["project_overview"]
    state["project_overview_markdown"] = tempstate["message"]
    state["original_user_input"] = user_input
    return state

async def accept_project_overview(state) -> str:
    console.print("")
    console.print("🤵 [bold yellow]Project Manager:[/bold yellow]")
    console.print(Panel.fit(state["project_overview_markdown"], border_style="cyan"))
    console.print("")
    acceptance_input = render_user_input()
    project_overview = json.loads(state["project_overview"])
    temp_state = await run_improved_project_overview(project_overview,acceptance_input)
    while temp_state["classification"]["category"] != 2:
        console.print("🤵 [bold yellow]Project Manager:[/bold yellow]")
        console.print(Panel.fit(state["message"], border_style="cyan"))
        console.print("")
        acceptance_input = render_user_input()
        temp_state = await run_improved_project_overview(state["project_overview"],acceptance_input)
    state["project_overview"] = temp_state["project_overview"]
    return state

async def generate_file_listing(state):
    console.print("👩‍🏭 Architect generating initial file listing...")
    user_prompt = instructions_for_output
    new_state = await run_initial_files_listing_graph(
            user_prompt=user_prompt,
            system_prompt=FLSP,
            project_overview=state["project_overview"]
        )
    state["files_listing"] = new_state["files_listing"]
    return state

async def improved_file_listing(state):
    console.print(f"👩‍🏭 Architect improving file listing...")
    new_state = await run_improved_files_listing_graph(
            original_user_prompt=state["original_user_input"],
            system_prompt=FLIP,
            project_overview=state["project_overview"],
            files_listing=state["files_listing"]
        )
    state["files_listing"] = new_state["files_listing"]
    return state

async def responsibility(state,file_name):
    console.print(f"👩‍🏭 Architect generating responsibilities for file {file_name}...")
    new_state = await run_responsibility_graph(
            system_prompt=RESP,
            project_overview=state["project_overview"],
            files_listing=state["files_listing"],
            file_name=file_name
        )
    state["files_listing"] = new_state["files_listing"]
    return state

async def dependency_generation(
    state_with_responsibilities,
    partial_dependency_list,
    file_name
) -> dict:
    console.print(f"👩‍🏭 Architect generating dependencies for file {file_name}...")
    path = Path(__file__).parent.parent / "assets" / "files_listing_for_dependencies.pkl"
    joblib.dump(state_with_responsibilities["files_listing"], path)
    state = await run_dependency_graph(
        files_listing=state_with_responsibilities["files_listing"],
        partial_dependency_list=partial_dependency_list,
        file_name=file_name,
        system_prompt=DESP,
    )
    return state["dependencies_dict"]

async def class_generation(state,file_name):
    console.print(f"👩‍🏭 Architect generating classes for file {file_name}...")
    new_state = await run_initial_class_generation_graph(
            original_user_prompt=state["original_user_input"],
            system_prompt=CLSP,
            project_overview=state["project_overview"],
            files_listing=state["files_listing"],
            file_name=file_name
        )
    state["files_listing"] = new_state["files_listing"]
    state["classes"].append({"file_name": file_name, "classes": new_state["class_dict"]})
    return state

async def js_function_generation(state,file_name):
    console.print(f"👩‍🏭 Architect generating JS functions for file {file_name}...")
    new_state = await run_js_function_generation_graph(
            original_user_prompt=state["original_user_input"],
            system_prompt=JSSP,
            project_overview=state["project_overview"],
            files_listing=state["files_listing"],
            file_name=file_name
        )
    state["functions"].append({"file_name": file_name, "functions": new_state["function_dict"]})
    state["files_listing"] = new_state["files_listing"]
    return state

async def env_file_content_generation(state,file_name):
    new_state = await run_env_file_generation_graph(
            architecture_dict=state["architecture_dict"],
            file_name=file_name,
            system_prompt=ENSP,
        )
    env_file_content = new_state["env_file_content"]
    state["implementations_so_far"].append(env_file_content)
    return state

async def py_file_content_generation(state,file_name):
    new_state = await run_py_file_generation_graph(
            architecture_dict=state["architecture_dict"],
            file_name=file_name,
            system_prompt=PYSP,
            implementations_so_far=state["implementations_so_far"]
        )
    state["implementations_so_far"].append(new_state["py_file_content"])
    return state

async def js_file_content_generation(state,file_name):
    new_state = await run_js_file_generation_graph(
            architecture_dict=state["architecture_dict"],
            file_name=file_name,
            system_prompt=JSCSP,
            implementations_so_far=state["implementations_so_far"]
        )
    state["implementations_so_far"].append(new_state["js_file_content"])
    return state

async def css_file_content_generation(state,file_name):
    new_state = await run_css_file_generation_graph(
            architecture_dict=state["architecture_dict"],
            file_name=file_name,
            system_prompt=CSSP,
            implementations_so_far=state["implementations_so_far"]
        )
    state["implementations_so_far"].append(new_state["css_file_content"])
    return state

async def md_file_content_generation(state,file_name):
    new_state = await run_md_file_generation_graph(
        architecture_dict=state["architecture_dict"],
        file_name=file_name,
        system_prompt=MDSP,
        implementations_so_far=state["implementations_so_far"]
    )
    state["implementations_so_far"].append(new_state["md_file_content"])
    return state

async def html_file_content_generation(state,file_name):
    new_state = await run_html_file_generation_graph(
            architecture_dict=state["architecture_dict"],
            file_name=file_name,
            system_prompt=HTSP,
            implementations_so_far=state["implementations_so_far"]
        )
    state["implementations_so_far"].append(new_state["html_file_content"])
    return state

async def docker_file_content_generation(state,file_name):
    new_state = await run_docker_file_generation_graph(
            architecture_dict=state["architecture_dict"],
            file_name=file_name,
            system_prompt=DOSP,
            implementations_so_far=state["implementations_so_far"]
        )
    state["implementations_so_far"].append(new_state["docker_file_content"])
    return state

async def requirements_in_file_content_generation(state, files_listing):
    new_state = await run_requirements_in_file_generation_graph(
            files_listing=files_listing,
            system_prompt=RISP,
        )
    if new_state is None:
        print("❌ ERROR: run_requirements_in_file_generation_graph returned None!")
        return state
    requirements_text_list = []
    for requirement in new_state["requirements_in_file_content"]["requirements_in"]:
        requirements_text_list.append(f"{requirement['package_name']} # {requirement['description']}\n")
    requirements_text = "".join(requirements_text_list)
    state["implementations_so_far"].append({"file_name": "requirements.in", "content": requirements_text})
    return state

async def install_file_content_generation(state,file_name):
    new_state = await run_install_file_generation_graph(
            architecture_dict=state["architecture_dict"],
            implementations_so_far=state["implementations_so_far"],
            file_name=file_name,
            system_prompt=IFSP,
        )
    state["implementations_so_far"].append(new_state["install_file_content"]["install_file"])
    return state

async def pyproject_toml_file_content_generation(state,file_name):
    new_state = await run_pyproject_toml_file_generation_graph(
            architecture_dict=state["architecture_dict"],
            implementations_so_far=state["implementations_so_far"],
            file_name=file_name,
            system_prompt=PTSP,
        )
    state["implementations_so_far"].append(new_state["pyproject_toml_file_content"])
    return state

async def implement_file(state,file_name):
    if file_name == ".env":
        console.print(f"👩‍💻 Coder implementing file {file_name}...")
        state = await env_file_content_generation(state,file_name)
        fill_file(state["file_structure"],state["implementations_so_far"][-1])
        return state
    elif file_name.endswith(".py"):
        console.print(f"👩‍💻 Coder implementing file {file_name}...")
        state = await py_file_content_generation(state,file_name)
        fill_file(state["file_structure"], state["implementations_so_far"][-1])
        return state
    elif file_name.endswith(".js"):
        console.print(f"👩‍💻 Coder implementing file {file_name}...")
        state = await js_file_content_generation(state,file_name)
        fill_file(state["file_structure"], state["implementations_so_far"][-1])
        return state
    elif file_name.endswith(".css"):
        console.print(f"👩‍💻 Coder implementing file {file_name}...")
        state = await css_file_content_generation(state,file_name)
        fill_file(state["file_structure"], state["implementations_so_far"][-1])
        return state
    elif file_name.endswith(".md"):
        console.print(f"👩‍💻 Coder implementing file {file_name}...")
        state = await md_file_content_generation(state,file_name)
        fill_file(state["file_structure"], state["implementations_so_far"][-1])
        return state
    elif file_name.endswith(".html"):
        console.print(f"👩‍💻 Coder implementing file {file_name}...")
        state = await html_file_content_generation(state,file_name)
        fill_file(state["file_structure"], state["implementations_so_far"][-1])
        return state
    elif "docker" in file_name.lower():
        console.print(f"👩‍💻 Coder implementing file {file_name}...")
        state = await docker_file_content_generation(state,file_name)
        fill_file(state["file_structure"], state["implementations_so_far"][-1])
        return state
    elif "install" in file_name.lower():
        console.print(f"👩‍💻 Coder implementing file {file_name}...")
        state = await install_file_content_generation(state,file_name)
        fill_file(state["file_structure"], state["implementations_so_far"][-1])
        return state
    elif file_name == "pyproject.toml":
        console.print(f"👩‍💻 Coder implementing file {file_name}...")
        state = await pyproject_toml_file_content_generation(state,file_name)
        fill_file(state["file_structure"], state["implementations_so_far"][-1])
        return state
    else:
        console.print(f"⚠️  Skipping unhandled file type: {file_name}")
        return state

class DevteamState(TypedDict, total=False):
    project_overview: dict
    project_overview_markdown: str
    files_listing: list
    clean_files_listing: list
    dependencies: list
    classes: list
    functions: list
    architecture_dict: dict
    file_structure: dict
    implementations_so_far: list
    message: str
    original_user_input: str

def create_master_graph(console=None):
    g = StateGraph(DevteamState, name="DevteamMasterGraph")
    async def user_input(state):
        new_state = await conversation_start(state)
        save_checkpoint(new_state, "UserInput")
        return new_state
    async def project_overview(state):
        new_state = await accept_project_overview(state)
        save_checkpoint(new_state, "ProjectOverview")
        return new_state
    async def file_listing(state):
        new_state = await generate_file_listing(state)
        new_state = await improved_file_listing(new_state)
        state["files_listing"] = new_state["files_listing"]
        state["clean_files_listing"] = state["files_listing"].copy()
        save_checkpoint(new_state, "FileListing")
        return state
    async def responsibilities(state):
        files = get_file_names(state["clean_files_listing"])
        for f in files:
            state = await responsibility(state, f)
        save_checkpoint(state, "Responsibilities")
        return state
    async def dependencies(state):
        files = get_file_names(state["clean_files_listing"])
        deps = []
        for f in files:
            partial = await dependency_generation(state, deps, f)
            deps.append({"file_name": f, "used_by": partial["used_by"]})
        state["dependencies"] = remove_circular_dependencies(deps)
        save_checkpoint(state, "Dependencies")
        return state
    async def classes(state):
        py_files = get_file_list_for_class_generation(state["clean_files_listing"])
        state["classes"] = []
        for f in py_files:
            state = await class_generation(state, f)
        save_checkpoint(state, "Classes")
        return state
    async def js_functions(state):
        js_files = get_file_list_for_js_function_generation(state["clean_files_listing"])
        state["functions"] = []
        for f in js_files:
            state = await js_function_generation(state, f)
        save_checkpoint(state, "JSFunctions")
        return state
    async def architecture(state):
        state["architecture_dict"] = get_architecture_dict(
            project_overview=state["project_overview"],
            files_listing=state["files_listing"],
            dependencies=state["dependencies"],
            classes=state["classes"],
            functions=state["functions"],
        )
        path = Path(__file__).parent.parent / "assets" / "architecture_dict.pkl"
        joblib.dump(state["architecture_dict"], path)
        arch_msg, file_structure = architecture_finished_message(state["architecture_dict"])
        state["file_structure"] = file_structure
        save_checkpoint(state, "Architecture")
        return state
    
    async def implementation(state):
        arch = state["architecture_dict"]
        deps = state["dependencies"]
        order = get_implementation_order(arch["files_listing"], deps)
        state["implementations_so_far"] = state.get("implementations_so_far", [])

        # 🔄 Resume if partial checkpoint exists
        checkpoint = load_file_checkpoint()
        completed = set()
        if checkpoint and "last_file" in checkpoint:
            last_done = checkpoint["last_file"]
            idx = order.index(last_done)
            completed = set(order[: idx + 1])
            console.print(f"🔁 Resuming from checkpoint after {last_done}")
        else:
            console.print("🚀 Starting fresh implementation phase...")

        for f in order:
            if f in completed:
                continue

            try:
                state = await implement_file(state, f)
                if state is None:
                    raise RuntimeError(f"implement_file returned None for {f}")

                # ✅ File-level checkpoint
                save_file_checkpoint(state, f)

            except Exception as e:
                console.print(f"❌ Error during implementation of {f}: {e}")
                raise

        # 🔚 Final node-level checkpoint when all files done
        save_checkpoint(state, "Implementation")
        return state

    
    # async def implementation(state):
    #     arch = state["architecture_dict"]
    #     deps = state["dependencies"]
    #     order = get_implementation_order(arch["files_listing"], deps)
    #     state["implementations_so_far"] = []
    #     for f in order:
    #         state = await implement_file(state, f)
    #         if state is None:
    #             raise RuntimeError(f"implement_file returned None for {f}")
    #     return state

    g.add_node("UserInput", user_input)
    g.add_node("ProjectOverview", project_overview)
    g.add_node("FileListing", file_listing)
    g.add_node("Responsibilities", responsibilities)
    g.add_node("Dependencies", dependencies)
    g.add_node("Classes", classes)
    g.add_node("JSFunctions", js_functions)
    g.add_node("Architecture", architecture)
    g.add_node("Implementation", implementation)

    g.add_edge("UserInput", "ProjectOverview")
    g.add_edge("ProjectOverview", "FileListing")
    g.add_edge("FileListing", "Responsibilities")
    g.add_edge("Responsibilities", "Dependencies")
    g.add_edge("Dependencies", "Classes")
    g.add_edge("Classes", "JSFunctions")
    g.add_edge("JSFunctions", "Architecture")
    g.add_edge("Architecture", "Implementation")

    g.set_entry_point("UserInput")
    g.set_finish_point("Implementation")

    return g

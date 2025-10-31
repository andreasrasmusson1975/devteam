from devteam.schemas.schema_creation import *
from devteam.system_prompts.system_prompts import *
from devteam.config.config import *
from devteam.api_call_functionality.api_calls import *
from markdown_pdf import MarkdownPdf, Section
from collections import defaultdict, deque
from typing import List, Dict, Set, Tuple
import json
import asyncio
import joblib
from pathlib import Path
from datetime import datetime
import os

def validate_chat_response(response: str, schema: SchemaCreator) -> bool:
    return schema.validate(response)

def project_overview_to_markdown(project_overview: dict) -> list:
    lines = []
    if "project_name" in project_overview:
        lines.append(f"[bold cyan]{project_overview['project_name']} - Project Overview[/bold cyan]\n")

    if "project_description" in project_overview:
        lines.append(f"[italic cyan]  Description:[/italic cyan]\n")
        lines.append(f"  {project_overview['project_description']}\n")

    list_fields = {
        "main_goals": "[italic cyan]  Main Goals:[/italic cyan]\n",
        "frameworks_and_technologies": "[italic cyan]  Frameworks & Technologies:[/italic cyan]\n",
        "security_goals": "[italic cyan]  Security Goals:[/italic cyan]\n",
        "security_considerations": "[italic cyan]  Security Considerations:[/italic cyan]\n",
        "notes": "[italic cyan]  Notes:[/italic cyan]\n",
    }

    for key, header in list_fields.items():
        if key in project_overview and project_overview[key]:
            lines.append(header)
            for item in project_overview[key]:
                if isinstance(item, dict):
                    lines.append(f"    [bold underline yellow]{item.get('name')}[/bold underline yellow]\n")
                    lines.append(f"    [italic green]Description:[/italic green]\n    {item.get('description')}\n")
                    lines.append(f"    [italic green]Reason for inclusion:[/italic green]\n    {item.get('reason for inclusion')}\n")
                else:
                    lines.append(f"    - {item}")
            lines.append("")
    return lines

def get_file_names(files_listing):
    file_names = []
    file_names.append(files_listing["environment_file"]["file_name"])
    file_names.append(files_listing["readme_file"]["file_name"])
    file_names.append(files_listing["entrypoint_file"]["file_name"])
    file_names.append(files_listing["pyproject_toml_file"]["file_name"])
    file_names.append(files_listing["install_sh"]["file_name"])
    file_names.append(files_listing["install_bat"]["file_name"])
    file_names.append(files_listing["config_file"]["file_name"])
    for file in files_listing["core_folder"]:
        file_names.append(file["file_name"])
    for file in files_listing["services_folder"]:
        file_names.append(file["file_name"])
    for file in files_listing["models_folder"]:
        file_names.append(file["file_name"])
    for file in files_listing["utils_folder"]:
        file_names.append(file["file_name"])
    for file in files_listing["adapters_folder"]:
        file_names.append(file["file_name"])
    for file in files_listing["assets_folder"]:
        file_names.append(file["file_name"])
    for file in files_listing["app_package"]["files"]:
        file_names.append(file["file_name"])
    for file in files_listing["static_folder"]["js_files"]:
        file_names.append(file["file_name"])
    for file in files_listing["static_folder"]["css_files"]:
        file_names.append(file["file_name"])
    for file in files_listing["templates_folder"]:
        file_names.append(file["file_name"])
    for file in files_listing["log_files"]:
        file_names.append(file["file_name"])
    for file in files_listing["documentation_files"]:
        file_names.append(file["file_name"])
    for file in files_listing["docker_files"]:
        file_names.append(file["file_name"])
    for file in files_listing["tests_folder"]:
        file_names.append(file["file_name"])
    return file_names

def get_file_list_for_class_generation(
        file_listing: dict
) -> str:
    file_names = []
    file_names = get_file_names(file_listing)
    condition = lambda s: (
        s.endswith(".py") and
        not s.endswith("__init__.py")
    )
    file_names = [name for name in file_names if condition(name)]
    return file_names

def get_file_list_for_js_function_generation(
        file_listing: dict
) -> str:
    file_names = []
    file_names = get_file_names(file_listing)
    condition = lambda s: (
        s.endswith(".js")
    )
    file_names = [name for name in file_names if condition(name)]
    return file_names

def add_responsibilities(files_listing: dict, file_name: str, responsibilities: list[str]) -> dict:
    def recursive_update(obj):
        if isinstance(obj, list):
            for item in obj:
                recursive_update(item)
        elif isinstance(obj, dict):
            if obj.get("file_name") == file_name:
                obj["responsibilities"] = responsibilities
            else:
                for v in obj.values():
                    recursive_update(v)

    recursive_update(files_listing)
    return files_listing



def remove_circular_dependencies(dependencies: List[Dict[str, List[str]]]) -> List[Dict[str, List[str]]]:
    row_nodes: Set[str] = {row["file_name"] for row in dependencies}

    adj: Dict[str, Set[str]] = defaultdict(set)
    all_nodes: Set[str] = set(row_nodes)
    for row in dependencies:
        dep = row["file_name"]
        for user in row.get("used_by", []):
            adj[dep].add(user)
            all_nodes.add(user)

    for n in all_nodes:
        adj.setdefault(n, set())

    UNVISITED, VISITING, DONE = 0, 1, 2
    state: Dict[str, int] = {n: UNVISITED for n in all_nodes}
    removed_edges: Set[Tuple[str, str]] = set()

    def dfs(u: str):
        state[u] = VISITING
        for v in list(adj[u]):
            if u == v:
                adj[u].remove(v)
                removed_edges.add((u, v))
                continue
            if state[v] == UNVISITED:
                dfs(v)
            elif state[v] == VISITING:
                adj[u].remove(v)
                removed_edges.add((u, v))
        state[u] = DONE

    for n in sorted(all_nodes):  # sort for determinism
        if state[n] == UNVISITED:
            dfs(n)

    cleaned: List[Dict[str, List[str]]] = []
    for row in dependencies:
        dep = row["file_name"]
        used_by = sorted(adj.get(dep, set()))
        cleaned.append({"file_name": dep, "used_by": used_by})

    return cleaned

    
def add_dependencies(files_listing: dict, file_name: str, dependencies: list[str]) -> dict:
    def recursive_update(obj):
        if isinstance(obj, list):
            for item in obj:
                recursive_update(item)
        elif isinstance(obj, dict):
            if obj.get("file_name") == file_name:
                obj["used_by"] = dependencies
            else:
                for v in obj.values():
                    recursive_update(v)

    recursive_update(files_listing)
    return files_listing

def add_classes(files_listing: dict, file_name: str, classes: list[dict]) -> dict:
    def recursive_update(obj):
        if isinstance(obj, list):
            for item in obj:
                recursive_update(item)
        elif isinstance(obj, dict):
            if obj.get("file_name") == file_name:
                obj["classes"] = classes["classes"]
            else:
                for v in obj.values():
                    recursive_update(v)

    recursive_update(files_listing)
    return files_listing

def add_js_functions(files_listing: dict, file_name: str, functions: list[dict]) -> dict:
    def recursive_update(obj):
        if isinstance(obj, list):
            for item in obj:
                recursive_update(item)
        elif isinstance(obj, dict):
            if obj.get("file_name") == file_name:
                obj["functions"] = functions["functions"]
            else:
                for v in obj.values():
                    recursive_update(v)

    recursive_update(files_listing)
    return files_listing

def get_architecture_dict(
    project_overview: dict,
    files_listing: dict,
    dependencies: list[dict],
    classes: list[dict],
    functions: list[dict]
) -> dict:
    architecture = {}
    architecture["project_overview"] = project_overview
    for dependency_entry in dependencies:
        files_listing = add_dependencies(
            files_listing,
            dependency_entry["file_name"],
            dependency_entry["used_by"]
        )
    for class_entry in classes:
        files_listing = add_classes(
            files_listing,
            class_entry["file_name"],
            class_entry["classes"]
        )
    for function_entry in functions:
        files_listing = add_js_functions(
            files_listing,
            function_entry["file_name"],
            function_entry["functions"]
        )
    architecture["files_listing"] = files_listing
    return architecture
    
def generate_architecture_markdown(architecture: dict) -> str:
    def generate_file_tree(folder_path: str) -> list[str]:
        folder = Path(folder_path)
        if not folder.is_dir():
            raise ValueError(f"{folder_path!r} is not a directory")

        tree_lines = [folder.name + "/"]

        def walk(dir_path: Path, prefix: str = ""):
            entries = sorted(dir_path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
            count = len(entries)
            for idx, entry in enumerate(entries):
                connector = "└─ " if idx == count - 1 else "├─ "
                tree_lines.append(f"{prefix}{connector}{entry.name}")
                if entry.is_dir():
                    extension = "   " if idx == count - 1 else "│  "
                    walk(entry, prefix + extension)

        walk(folder)
        return "\n".join(tree_lines)
    
    def get_no_classes_or_functions(
        file_dict: dict,
        lines: list[str]
    ):
        lines.append(f"### File: {file_dict['file_name']}\n")
        lines.append("#### *Description*\n")
        lines.append(f"  {file_dict['file_description']}\n")
        lines.append("#### *Responsibilities*\n")
        for responsibility in file_dict['responsibilities']["responsibilities"]:
            lines.append(f"  - {responsibility}\n")
        if file_dict.get("used_by", None) is not None:
            lines.append("#### *Used By*\n")
            if file_dict['used_by']:
                for user in file_dict['used_by']:
                    lines.append(f"  - {user}\n")
            else:
                lines.append("  - None\n")
    def get_with_classes(
        file_dict: dict,
        lines: list[str]
    ):
        get_no_classes_or_functions(file_dict, lines)
        lines.append("#### *Classes*\n")
        for class_entry in file_dict['classes']:
            lines.append(f"##### {class_entry['class_name']}\n")
            lines.append(f"  {class_entry['class_description']}\n")
            lines.append("  *Attributes:*\n")
            for attribute in class_entry['attributes']:
                lines.append(f"  - {attribute['attribute_name']} ({attribute['attribute_type']}): {attribute['attribute_description']}\n")
            lines.append("  *Methods:*\n")
            for method in class_entry['methods']:
                lines.append(f"  - {method['method_name']}({', '.join([param['parameter_name'] + ': ' + param['parameter_type'] for param in method['parameters']])}) -> {method['return_type']}: {method['method_description']}\n")
    
    def get_core(
        files_list: list[dict],
        lines: list[str]
    ):
        lines.append("#### Folder: core\n")
        for file in files_list:
            get_with_classes(
                file,
                lines
            )

    def get_services(
        files_list: list[dict],
        lines: list[str]
    ):
        lines.append("#### Folder: services\n")
        for file in files_list:
            get_with_classes(
                file,
                lines
            )

    def get_models(
        files_list: list[dict],
        lines: list[str]
    ):
        lines.append("#### Folder: models\n")
        for file in files_list:
            get_with_classes(
                file,
                lines
            )
    
    def get_utils(
        files_list: list[dict],
        lines: list[str]
    ):
        lines.append("#### Folder: utils\n")
        for file in files_list:
            get_with_classes(
                file,
                lines
            )
    
    def get_adapters(
        files_list: list[dict],
        lines: list[str]
    ):
        lines.append("#### Folder: adapters\n")
        for file in files_list:
            get_with_classes(
                file,
                lines
            )
    
    def get_assets(
        files_list: list[dict],
        lines: list[str]
    ):
        lines.append("#### Folder: assets\n")
        for file in files_list:
            get_no_classes_or_functions(
                file,
                lines
            )

    def get_app_package(
        files_dict: dict,
        lines: list[str]
    ):
        lines.append("#### Folder: app\n")
        for file in files_dict['files']:
            get_with_classes(
                file,
                lines
            )
    def get_with_js_functions(
        file_dict: dict,
        lines: list[str]
    ):
        get_no_classes_or_functions(file_dict, lines)
        lines.append("##### *Functions*\n")
        for function in file_dict['functions']:
            lines.append(f"  - {function['function_name']}({', '.join([param['parameter_name'] + ': ' + param['parameter_type'] for param in function['parameters']])}) -> {function['return_type']}: {function['function_description']}\n")
        
    def get_static_folder(
        folder_dict: dict,
        lines: list[str]
    ):
        lines.append("#### Folder: static\n")
        lines.append("##### Folder: js_files\n")
        for file in folder_dict["js_files"]:
            get_with_js_functions(
                file,
                lines
            )
    lines = []
    lines.append(f"# Architecture - {architecture['project_overview']['project_name']}\n")
    lines.append("## Project Description\n")
    lines.append(architecture["project_overview"]["project_description"] + "\n")
    lines.append("## Project Overview\n")
    lines.append("### Main Goals\n")
    for item in architecture["project_overview"]["main_goals"]:
        lines.append(f"- {item}\n")
    lines.append("### Frameworks & Technologies\n")
    for item in architecture["project_overview"]["frameworks_and_technologies"]:
        lines.append("#### *" + item["name"] + "*\n")
        lines.append(f"##### Description\n {item['description']}\n")
        lines.append(f"##### Reason for inclusion\n {item['reason for inclusion']}\n")
    lines.append("### Security Goals\n")
    for item in architecture["project_overview"]["security_goals"]:
        lines.append(f"- {item}\n")
    lines.append("### Notes\n")
    for item in architecture["project_overview"]["notes"]:
        lines.append(f"- {item}\n")
    lines.append("\n## Files And Folders")
    lines.append("### File Tree\n")
    path = architecture["project_overview"]["project_name"].lower().replace(" ", "_")
    lines.append("```bash\n" + generate_file_tree(path) + "\n```\n")
    get_no_classes_or_functions(
        architecture["files_listing"]["environment_file"],
        lines
    )
    get_no_classes_or_functions(
        architecture["files_listing"]["pyproject_toml_file"],
        lines
    )
    get_no_classes_or_functions(
        architecture["files_listing"]["readme_file"],
        lines
    )
    get_no_classes_or_functions(
        architecture["files_listing"]["install_sh"],
        lines
    )
    get_with_classes(
        architecture["files_listing"]["entrypoint_file"],
        lines
    )
    get_with_classes(
        architecture["files_listing"]["config_file"],
        lines
    )
    get_core(
        architecture["files_listing"]["core_folder"],
        lines
    )
    get_services(
        architecture["files_listing"]["services_folder"],
        lines
    )
    get_models(
        architecture["files_listing"]["models_folder"],
        lines
    )
    get_utils(
        architecture["files_listing"]["utils_folder"],
        lines
    )
    get_adapters(
        architecture["files_listing"]["adapters_folder"],
        lines
    )
    get_assets(
        architecture["files_listing"]["assets_folder"],
        lines
    )
    get_app_package(
        architecture["files_listing"]["app_package"],
        lines
    )
    get_static_folder(
        architecture["files_listing"]["static_folder"],
        lines
    )
    lines.append("#### Folder: css\n")
    for file in architecture["files_listing"]["static_folder"]["css_files"]:
        get_no_classes_or_functions(
            file,
            lines
        )
    lines.append("#### Folder: templates\n")
    for file in architecture["files_listing"]["templates_folder"]:
        get_no_classes_or_functions(
            file,
            lines
        )
    lines.append("#### Folder: tests\n")
    for file in architecture["files_listing"]["tests_folder"]:
        get_with_classes(
            file,
            lines
        )
    lines.append("#### Folder: logging\n")
    for file in architecture["files_listing"]["log_files"]:
        if file.get("classes",[]):
            get_with_classes(
                file,
                lines
            )
        else:
            get_no_classes_or_functions(
                file,
                lines
            )
    lines.append("#### Folder: doc\n")
    for file in architecture["files_listing"]["documentation_files"]:
        get_no_classes_or_functions(
            file,
            lines
        )
    lines.append("#### Folder: docker\n")
    for file in architecture["files_listing"]["docker_files"]:
        get_no_classes_or_functions(
            file,
            lines
        )
    lines.append("## Summary\n")
    lines.append(architecture["files_listing"]["integration_summary"] + "\n")

    return "\n".join(lines)

def save_architecture_to_file(markdown: str, architecture: dict):
    project_name = architecture["project_overview"]["project_name"].lower().replace(" ", "_")
    save_path = Path().cwd() / project_name / "docs" / "architecture.pdf"
    with open(Path(__file__).parent / "pdf.css", "r") as f:
        css = f.read()
    pdf = MarkdownPdf(toc_level=2)
    parts = markdown.split("## Files And Folders")
    pdf.add_section(Section(parts[0]),user_css=css)
    if len(parts) > 1:
        pdf.add_section(Section("## Files And Folders" + parts[1]),user_css=css)
    pdf.save(save_path)

def get_implementation_order(files_listing: dict, dependencies: list) -> list[str]:
    deps = {}
    for elem in dependencies:
        deps[elem["file_name"]] = elem["used_by"]
    def get_accumulated_in_degree(file_name):
        if not deps[file_name]:
            return 0
        for user in deps[file_name]:
            return 1 + sum(get_accumulated_in_degree(user) for user in deps[file_name])
    in_degrees = []   
    for entry in dependencies:
        in_degree = get_accumulated_in_degree(entry["file_name"])
        in_degrees.append((entry["file_name"], in_degree))
    in_degrees.sort(key=lambda x: x[1], reverse=True)
    implementation_order = [str(file[0]) for file in in_degrees]
    env_file = [entry for entry in implementation_order if entry.endswith(".env")]
    config_file = [entry for entry in implementation_order if entry == "config.py"]
    md_files = [entry for entry in implementation_order if entry.endswith(".md")]
    css_files = [entry for entry in implementation_order if entry.endswith(".css")]
    js_files = [entry for entry in implementation_order if entry.endswith(".js")]
    py_files = [entry for entry in implementation_order if entry.endswith(".py") and entry not in ["config.py", "run.py"]]
    run_file = [entry for entry in implementation_order if entry == "run.py"]
    docker_files = [entry for entry in implementation_order if "docker" in entry.lower()]
    install_files = [entry for entry in implementation_order if "install" in entry.lower()]
    html_files = [entry for entry in implementation_order if entry.endswith(".html")]
    pyproject_toml_file = [entry for entry in implementation_order if entry == "pyproject.toml"]
    implementation_order = []
    implementation_order.extend(env_file)
    implementation_order.extend(config_file)
    implementation_order.extend(css_files)
    implementation_order.extend(py_files)
    implementation_order.extend(js_files)
    implementation_order.extend(html_files)
    implementation_order.extend(docker_files)
    implementation_order.extend(pyproject_toml_file)
    implementation_order.extend(install_files)
    implementation_order.extend(run_file)
    implementation_order.extend(md_files)
    return implementation_order

def parse_env_file_content(env_file_content: dict) -> str:
    lines = []
    for env_var in env_file_content["content"]:
        lines.append(f"# Description: {env_var['description and purpose']}")
        lines.append(f"# Example Value: {env_var['example_value']}")
        lines.append(f"{env_var['env_variable_name']}\n")
    return "\n".join(lines)

def generate_project_tree(root_folder: str, max_depth: int = 6, ignore_hidden: bool = False) -> str:
    root = Path(root_folder).resolve()
    tree_lines = [f"{root.name}/"]

    def _walk(dir_path: Path, prefix: str = "", depth: int = 0):
        if depth >= max_depth:
            tree_lines.append(f"{prefix}└── … (max depth reached)")
            return

        entries = sorted(
            [p for p in dir_path.iterdir() if not (ignore_hidden and p.name.startswith("."))],
            key=lambda x: (x.is_file(), x.name.lower())
        )
        for i, entry in enumerate(entries):
            connector = "└── " if i == len(entries) - 1 else "├── "
            tree_lines.append(f"{prefix}{connector}{entry.name}")
            if entry.is_dir():
                new_prefix = prefix + ("    " if i == len(entries) - 1 else "│   ")
                _walk(entry, new_prefix, depth + 1)

    _walk(root)
    return "\n".join(tree_lines)

def fill_file(file_structure: list,content: dict):
    for file_path in file_structure:
        file_name = file_path.name
        if file_name == content["file_name"]:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content["content"])

#### Checkpointing Helpers ####

CHECKPOINT_FILE = Path("devteam_checkpoint.pkl")

def save_checkpoint(state, node_name):
    """Save current graph state and node name to disk."""
    data = {"state": state, "last_node": node_name}
    joblib.dump(data, CHECKPOINT_FILE)
    print(f"💾 Saved checkpoint after '{node_name}'.")

def load_checkpoint():
    """Load the latest checkpoint if it exists."""
    if CHECKPOINT_FILE.exists():
        data = joblib.load(CHECKPOINT_FILE)
        print(f"🔄 Loaded checkpoint from node '{data['last_node']}'.")
        return data["state"], data["last_node"]
    return None, None

def clear_checkpoint():
    """Remove the checkpoint file."""
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()
        print("🧹 Cleared checkpoint.")

def save_file_checkpoint(state, file_name):
    path = "file_generation.pkl"

    checkpoint = {
        "last_file": file_name,
        "timestamp": datetime.now().isoformat(),
        "implementations_so_far": state.get("implementations_so_far", []),
    }
    joblib.dump(checkpoint, path)
    print(f"💾 Saved checkpoint after '{file_name}'.")

def load_file_checkpoint():
    path = "file_generation.pkl"
    if os.path.exists(path):
        return joblib.load(path)
    return None

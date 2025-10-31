import os
from pathlib import Path
def create_file_structure(architecture: dict) -> dict:
    file_structure = []
    root_dir = Path(architecture["project_overview"]["project_name"].lower().replace(" ", "_"))
    source_dir = root_dir / "src"
    core_dir = source_dir / "core"
    services_dir = source_dir / "services"
    utils_dir = source_dir / "utils"
    models_dir = source_dir / "models"
    adapters_dir = source_dir / "adapters"
    assets_dir = source_dir / "assets"
    app_dir = source_dir / "app"
    static_dir = source_dir / "static"
    templates_dir = source_dir / "templates"
    js_dir = static_dir / "js"
    css_dir = static_dir / "css"
    tests_dir = root_dir / "tests"
    log_dir = source_dir / "app_logging"
    docs_folder = root_dir / "docs"
    docker_dir = source_dir / "docker"

    env_file = source_dir / ".env" 
    readme_file = root_dir / "README.md"
    entry_point_file = source_dir / "run.py"
    pyproject_toml_file = root_dir / "pyproject.toml"
    install_sh = root_dir / "install.sh"
    install_bat = root_dir / "install.bat"
    config_file = source_dir / "config.py"

    os.makedirs(root_dir, exist_ok=True)
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(core_dir, exist_ok=True)
    os.makedirs(services_dir, exist_ok=True)
    os.makedirs(utils_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(adapters_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(app_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(js_dir, exist_ok=True)
    os.makedirs(css_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(docs_folder, exist_ok=True)
    os.makedirs(docker_dir, exist_ok=True)

    env_file.touch(exist_ok=True)
    file_structure.append(env_file)
    readme_file.touch(exist_ok=True)
    file_structure.append(readme_file)
    entry_point_file.touch(exist_ok=True)
    file_structure.append(entry_point_file)
    pyproject_toml_file.touch(exist_ok=True)
    file_structure.append(pyproject_toml_file)
    install_sh.touch(exist_ok=True)
    file_structure.append(install_sh)
    install_bat.touch(exist_ok=True)
    file_structure.append(install_bat)
    config_file.touch(exist_ok=True)
    file_structure.append(config_file)
    for file in architecture["files_listing"]["core_folder"]:
        file_path = core_dir / file["file_name"]
        file_path.touch(exist_ok=True)
        file_structure.append(file_path)
    for file in architecture["files_listing"]["services_folder"]:
        file_path = services_dir / file["file_name"]
        file_path.touch(exist_ok=True)
        file_structure.append(file_path)
    for file in architecture["files_listing"]["utils_folder"]:
        file_path = utils_dir / file["file_name"]
        file_path.touch(exist_ok=True)
        file_structure.append(file_path)
    for file in architecture["files_listing"]["models_folder"]:
        file_path = models_dir / file["file_name"]
        file_path.touch(exist_ok=True)
        file_structure.append(file_path)
    for file in architecture["files_listing"]["adapters_folder"]:
        file_path = adapters_dir / file["file_name"]
        file_path.touch(exist_ok=True)
        file_structure.append(file_path)
    for file in architecture["files_listing"]["assets_folder"]:
        file_path = assets_dir / file["file_name"]
        file_path.touch(exist_ok=True)
        file_structure.append(file_path)
    for file in architecture["files_listing"]["app_package"]["files"]:
        file_path = app_dir / file["file_name"]
        file_path.touch(exist_ok=True)
        file_structure.append(file_path)
    for file in architecture["files_listing"]["static_folder"]["js_files"]:
        file_path = js_dir / file["file_name"]
        file_path.touch(exist_ok=True)
        file_structure.append(file_path)
    for file in architecture["files_listing"]["static_folder"]["css_files"]:
        file_path = css_dir / file["file_name"]
        file_path.touch(exist_ok=True)
        file_structure.append(file_path)
    for file in architecture["files_listing"]["templates_folder"]:
        file_path = templates_dir / file["file_name"]
        file_path.touch(exist_ok=True)
        file_structure.append(file_path)
    for file in architecture["files_listing"]["tests_folder"]:
        file_path = tests_dir / file["file_name"]
        file_path.touch(exist_ok=True)
        file_structure.append(file_path)
    for file in architecture["files_listing"]["log_files"]:
        file_path = log_dir / file["file_name"]
        file_path.touch(exist_ok=True)
        file_structure.append(file_path)
    for file in architecture["files_listing"]["documentation_files"]:
        file_path = docs_folder / file["file_name"]
        try:
            file_path.touch(exist_ok=True)
            file_structure.append(file_path)
        except Exception as e:
            print(architecture["files_listing"]["documentation_files"])
            print(f"Error creating file {file_path}: {e}")
    for file in architecture["files_listing"]["docker_files"]:
        file_path = docker_dir / file["file_name"]
        file_path.touch(exist_ok=True)
        file_structure.append(file_path)
    recursive_add_init_files(source_dir)
    return file_structure

def recursive_add_init_files(directory: Path):
    init_file = directory / "__init__.py"
    init_file.touch(exist_ok=True)
    for item in directory.iterdir():
        if item.is_dir():
            recursive_add_init_files(item)
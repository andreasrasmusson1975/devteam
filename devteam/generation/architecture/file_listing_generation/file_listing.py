from devteam.api_call_functionality.api_calls import get_chat_response
from devteam.schemas.schema_creation import *
from devteam.system_prompts.system_prompts import *
from devteam.helper_functionality.helpers import *
from devteam.decorators.decorators import retry
from devteam.config.config import *
import asyncio
import copy

instructions_for_output = [
    {
        "output_section_name": "environment_file",
        "section_mandatory": True,
        "allowed_file_endings": [".env"],
        "instructions": [
            "The environment file MUST be named '.env'.",
            "It contains key-value pairs for all environment variables needed in the application."
        ]
    },
    {
        "output_section_name": "readme_file",
        "section_mandatory": True,
        "allowed_file_endings": [".md"],
        "instructions": [
            "The README file MUST be named 'README.md'.",
            "It should describe the project purpose, setup instructions, and how to run the web app."
        ]
    },
    {
        "output_section_name": "entrypoint_file",
        "section_mandatory": True,
        "allowed_file_endings": [".py"],
        "instructions": [
            "The entrypoint file MUST be named 'run.py'.",
            "It is the only file that should be executed to start the application.",
        ]
    },
    {
        "output_section_name": "install_sh",
        "section_mandatory": True,
        "allowed_file_endings": [".sh"],
        "instructions": [
            "The install.sh file MUST be named 'install.sh'.",
            "It is a bash script to set up the development environment on Unix-based systems."
        ]
    },
    {
        "output_section_name": "install_bat",
        "section_mandatory": True,
        "allowed_file_endings": [".bat"],
        "instructions": [
            "The install.bat file MUST be named 'install.bat'.",
            "It is a batch script to set up the development environment on Windows systems."
        ]
    },
    {
        "output_section_name": "config_file",
        "section_mandatory": True,
        "allowed_file_endings": [".py"],
        "instructions": [
            "The config file MUST be named 'config.py'.",
            "It loads environment variables, sets constants, and provides application configuration classes."
        ]
    },
    {
        "output_section_name": "pyproject_toml_file",
        "section_mandatory": True,
        "allowed_file_endings": [".toml"],
        "instructions": [
            "The pyproject.toml file MUST be named 'pyproject.toml'.",
            "It will contain the project's metadata and dependencies."
        ]
    },
    {
        "output_section_name": "core_folder",
        "section_mandatory": True,
        "allowed_file_endings": [".py"],
        "instructions": [
            "This folder MUST be named 'core'.",
            "It contains core functionalities specific to the application's domain.",
            "Do NOT create subfolders here; keep all core files directly in the 'core' folder.",
            "Do NOT include general utilities here; they have their own section.",
            "Do NOT include database functionality here; they have their own section.",
            "Do NOT include logging functionality here; it should be in the logs section."
            "Do not include web framework related files here; they have their own section."
        ]
    },
    {
        "output_section_name": "services_folder",
        "section_mandatory": True,
        "allowed_file_endings": [".py"],
        "instructions": [
            "This folder MUST be named 'services'.",
            "It contains service layer code that handles business logic and interacts with core functionalities.",
            "Do NOT create subfolders here; keep all service files directly in the 'services' folder.",
            "Do NOT include general utilities here; they have their own section.",
            "Do NOT include database functionality here; they have their own section.",
            "Do NOT include logging functionality here; it should be in the logs section."
            "Do not include web framework related files here; they have their own section."
        ]
    },
    {
        "output_section_name": "models_folder",
        "section_mandatory": True,
        "allowed_file_endings": [".py"],
        "instructions": [
            "This folder MUST be named 'models'.",
            "It contains data models or schemas used in the application.",
            "Do NOT create subfolders here; keep all model files directly in the 'models' folder.",
            "Do NOT include general utilities here; they have their own section.",
            "Do NOT include database functionality here; they have their own section.",
            "Do NOT include logging functionality here; it should be in the logs section."
            "Do not include web framework related files here; they have their own section."
        ]
    },
    {
        "output_section_name": "utils_folder",
        "section_mandatory": True,
        "allowed_file_endings": [".py"],
        "instructions": [
            "This folder MUST be named 'utils'.",
            "It contains utility functions and helper modules used across the application.",
            "Do NOT create subfolders here; keep all utility files directly in the 'utils' folder.",
        ]
        
    },
    {
        "output_section_name": "adapters_folder",
        "section_mandatory": True,
        "allowed_file_endings": [".py"],
        "instructions": [
            "This folder MUST be named 'adapters'.",
            "It contains code for interacting with external systems, APIs, or databases.",
            "Do NOT create subfolders here; keep all adapter files directly in the 'adapters' folder.",
            "Do NOT include general utilities here; they have their own section.",
            "Do NOT include logging functionality here; it should be in the logs section."
            "Do NOT include core, service, or model logic here; they have their own sections."
            "Include web framework related files here."
            "Include database interaction files here."
        ]

    },
    {
        "output_section_name": "app_package",
        "section_mandatory": True,
        "allowed_file_endings": [".py"],
        "instructions": [
            "This folder MUST be named 'app'.",
            "It is the main application package containing the main application logic.",
            "It uses the core, services, models, utils, and adapters modules.",
            "Include all modules related to the application's primary functionality here.",
            "Do NOT create subfolders here; keep all app files directly in the 'app' folder.",
            "Do NOT include general utilities here; they have their own section.",
            "Do NOT include database functionality here; they have their own section.",
            "Do NOT include logging functionality here; it should be in the logs section."
            "Do not include web framework related files here; they have their own section."
        ]
    },
    {
        "output_section_name": "assets_folder",
        "section_mandatory": False,
        "allowed_file_endings": ["Any file endings allowed"],
        "instructions": [
            "This folder MAY be named 'assets'.",
            "It contains any additional assets needed for the application that do not fit into other categories.",
            "You can include images, fonts, or other media files here.",
            "You can include files that the application produces at runtime here, but not log files.",
        ]
    },
    {
        "output_section_name": "static_folder",
        "section_mandatory": True,
        "allowed_file_endings": [".js", ".css"],
        "instructions": [
            "This folder MUST be named 'static'.",
            "It contains frontend assets for the web UI.",
            "Do NOT include subfolders here; keep all static files directly in the 'static' folder.",
        ]
    },
    {
        "output_section_name": "templates_folder",
        "section_mandatory": True,
        "allowed_file_endings": [".html"],
        "instructions": [
            "This folder MUST be named 'templates'.",
            "It contains HTML templates used by the application.",
        ]
    },
    {
        "output_section_name": "tests_folder",
        "section_mandatory": True,
        "allowed_file_endings": [".py"],
        "instructions": [
            "This folder MUST be named 'tests'.",
            "It contains unit and integration tests for backend logic.",
            "Each test file MUST include a 'tested_module' field specifying which module it tests.",
            "Each module in the app package should have a corresponding test file named 'test_<module_name>.py'."
        ]
    },
    {
        "output_section_name": "log_files",
        "section_mandatory": True,
        "allowed_file_endings": [".log",".py"],
        "instructions": [
            "Include at least one .log file.",
            """Additionally, include a 'logger.py' file to configure logging. 
            The description of this file MUST be 'contains decorator functions for logging'.""",
        ]
    },
    {
        "output_section_name": "documentation_files",
        "section_mandatory": True,
        "allowed_file_endings": [".md"],
        "instructions": [
            "Include any additional documentation files needed to understand and use the application.",
            "Do not include the README.md here; it has its own section.",
            "Do not include ARCHITECTURE.md here; it has its own section.",
        ]
    },
    {
        "output_section_name": "docker_files",
        "section_mandatory": True,
        "allowed_file_endings": ["",".test",".yml"],
        "instructions": [
            "You MUST include a Dockerfile for containerizing the application.",
            "You MUST include a Dockerfile.test for running tests in a containerized environment.",
            "Optionally include any other necessary Docker-related files.",
        ]
    },
    {
        "output_section_name": "integration_summary",
        "section_mandatory": True,
        "allowed_file_endings": [],
        "instructions": [
            "Summarize how all files and components integrate to form the complete application.",
            "Describe key dependencies and module relationships."
        ]
    }
]

improved_file_listing_input = """
Based on the current file listing and the project overview, 
please make improvements to the file listing.
"""

def get_initial_file_listing_user_prompt(
    project_overview: str,
    schema: SchemaCreator
) -> str:
    user_prompt = {
        "project_overview": project_overview,
        "instructions_for_output": instructions_for_output
    }
    user_prompt = json.dumps(user_prompt, indent=4)
    if schema.validate(user_prompt):
        return user_prompt
    else:
        raise ValueError("User prompt does not conform to schema")

def get_improved_file_listing_user_prompt(
    original_user_prompt: str,
    project_overview: str,
    file_listing_input: str,
    schema: SchemaCreator
) -> str:
    user_prompt = {
        "original_user_prompt": original_user_prompt,
        "project_overview": project_overview,
        "generated_files_listing": file_listing_input,
        "instructions_for_output": instructions_for_output,
        "task": improved_file_listing_input
    }
    user_prompt = json.dumps(user_prompt, indent=4)
    if schema.validate(user_prompt):
        return user_prompt
    else:
        raise ValueError("User prompt does not conform to schema")
    
def normalize_file_names(files_listing: dict) -> dict:
    normalized_listing = files_listing
    normalized_listing["environment_file"]["file_name"] = ".env"
    normalized_listing["readme_file"]["file_name"] = "README.md"
    normalized_listing["entrypoint_file"]["file_name"] = "run.py"
    normalized_listing["install_sh"]["file_name"] = "install.sh"
    normalized_listing["install_bat"]["file_name"] = "install.bat"
    normalized_listing["config_file"]["file_name"] = "config.py"
    normalized_listing["pyproject_toml_file"]["file_name"] = "pyproject.toml"
    for core_file in normalized_listing["core_folder"]:
        core_file["file_name"] = Path(core_file["file_name"]).name
    for services_file in normalized_listing["services_folder"]:
        services_file["file_name"] = Path(services_file["file_name"]).name
    for models_file in normalized_listing["models_folder"]:
        models_file["file_name"] = Path(models_file["file_name"]).name
    for utils_file in normalized_listing["utils_folder"]:
        utils_file["file_name"] = Path(utils_file["file_name"]).name
    for adapters_file in normalized_listing["adapters_folder"]:
        adapters_file["file_name"] = Path(adapters_file["file_name"]).name
    for assets_file in normalized_listing["assets_folder"]:
        assets_file["file_name"] = Path(assets_file["file_name"]).name
    for static_file in normalized_listing["static_folder"]["js_files"]:
        static_file["file_name"] = Path(static_file["file_name"]).name
    for static_file in normalized_listing["static_folder"]["css_files"]:
        static_file["file_name"] = Path(static_file["file_name"]).name
    for template_file in normalized_listing["templates_folder"]:
        template_file["file_name"] = Path(template_file["file_name"]).name
    for app_file in normalized_listing["app_package"]["files"]:
        app_file["file_name"] = Path(app_file["file_name"]).name
    for test_file in normalized_listing["tests_folder"]:
        test_file["file_name"] = Path(test_file["file_name"]).name
    for log_file in normalized_listing["log_files"]:
        log_file["file_name"] = Path(log_file["file_name"]).name
    return normalized_listing

@retry(max_attempts=3, delay=1)
async def get_initial_files_listing(
    user_prompt: str,
) -> dict:
    try:
        response = await get_chat_response(
            system_prompt=FLSP,
            user_prompt=user_prompt,
            which_model=1,
            model_name= model_name,
        )
        validate_chat_response(response, get_files_listing_output_schema())
        response = json.loads(response)
        response = normalize_file_names(response)
        return response
    except Exception as e:
        raise #ValueError(f"Error in files listing generation: {e}")   

@retry(max_attempts=3, delay=1)
async def get_improved_files_listing(
    user_prompt: str,
) -> dict:
    try:
        response = await get_chat_response(
            system_prompt=FLIP,
            user_prompt=user_prompt,
            which_model=1,
            model_name= model_name,
        )
        validate_chat_response(response, get_files_listing_output_schema())
        response = json.loads(response)
        response = normalize_file_names(response)
        return response
    except Exception as e:
        raise ValueError(f"Error in improved files listing generation: {e}")    

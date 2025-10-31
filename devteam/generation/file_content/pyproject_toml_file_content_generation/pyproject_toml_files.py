from devteam.api_call_functionality.api_calls import get_chat_response
from devteam.schemas.schema_creation import *
from devteam.system_prompts.system_prompts import *
from devteam.helper_functionality.helpers import *
from devteam.config.config import *
from devteam.decorators.decorators import retry
import asyncio
import json

instructions=f"""
Generate the content of the pyproject.toml file for a Python project based on the provided architecture. 
The pyproject.toml file should include all necessary configurations and dependencies as indicated in the architecture.
Analyze the python files carefully to extract the required dependencies and settings.

The pyproject.toml file MUST:
1. Include the [build-system] section with the appropriate build backend and requirements.
2. Include the [tool.poetry] section with project metadata such as name, version, description, authors, and license.
3. List all dependencies under the [tool.poetry.dependencies] section.
4. List all development dependencies under the [tool.poetry.dev-dependencies] section.
5. Follow the TOML format strictly to ensure compatibility with package managers.

### HARD REQUIREMENT:
NEVER EVER generate mock content or placeholder content. The content MUST be a complete and 
functional implementation of the specified file. The content MUST be production ready.
"""

def get_pyproject_toml_user_prompt(
    architecture_dict: dict,
    implementations_so_far: list,
    file_name: str,
) -> str:
    user_prompt_dict = {
        "project_overview": architecture_dict["project_overview"],
        "files_listing": architecture_dict["files_listing"],
        "implementations_so_far": implementations_so_far,
        "file_to_implement": file_name,
        "project_tree": generate_project_tree(
            architecture_dict["project_overview"]["project_name"].lower().replace(" ", "_")
        ),
        "instructions": instructions
    }
    user_prompt = json.dumps(user_prompt_dict)
    schema = get_code_generation_input_schema()
    if schema.validate(user_prompt):
        return user_prompt
    else:
        raise ValueError("User prompt does not conform to schema")
    
@retry(max_attempts=3, delay=1)    
async def get_pyproject_toml_file_content(
    user_prompt: str,
    system_prompt
) -> dict:
    try:
        response = await get_chat_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        which_model=1,
        model_name= model_name,
        )
        validate_chat_response(response, get_pyproject_toml_generation_output_schema())
        response_dict = json.loads(response)
        return response_dict
    except Exception as e:
        print(f"Error in get_pyproject_toml_file_content: {e}")
        raise e
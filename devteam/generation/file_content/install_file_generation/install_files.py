from devteam.api_call_functionality.api_calls import get_chat_response
from devteam.schemas.schema_creation import *
from devteam.system_prompts.system_prompts import *
from devteam.helper_functionality.helpers import *
from devteam.config.config import *
from devteam.decorators.decorators import retry
import asyncio
import json

instructions=f"""
Generate the content of the install file. Analyze the provided architecture carefully to create
the install file with the necessary commands and configurations. You can infer the operating system
and environment from the file name. Please note that there is already a pyproject.toml file generated
that contains the project dependencies. In the install script, uv should be used to handle the installation of these dependencies.

The install script MUST:
1. Create a virtual environment using uv.
2. Install dependencies from pyproject.toml using uv.
3. Install the application in editable mode using uv.
4. Include any additional setup commands necessary for the project as indicated in the architecture.

### Important
- If generating a bat file, ensure to use call where necessary to allow the script to continue executing subsequent commands.
- If making changes or addition to PATH, be sure to export the updated PATH so that subsequent commands can access the newly added paths.

### HARD REQUIREMENT:
NEVER EVER generate mock content or placeholder content. The content MUST be a complete and 
functional implementation of the specified file. The content MUST be production ready.
"""

def get_install_file_user_prompt(
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
async def get_install_file_content(
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
        validate_chat_response(response, get_install_file_generation_output_schema())
        response_dict = json.loads(response)
        return response_dict
    except Exception as e:
        print(f"Error in get_install_file_content: {e}")
        raise e
from devteam.api_call_functionality.api_calls import get_chat_response
from devteam.schemas.schema_creation import *
from devteam.system_prompts.system_prompts import *
from devteam.helper_functionality.helpers import *
from devteam.config.config import *
from devteam.decorators.decorators import retry
import asyncio
import json
import copy

important_instructions = """
Pay special attention to the partial_dependencies_list when identifying dependencies for the specified file.
Use it to make sure that you NEVER introduce circular dependencies.

### HARD REQUIREMENT 1: NO CIRCULAR DEPENDENCIES
It must never happen that file A depends on file B, while file B also depends on file A. This is very
important and a hard requirement.

### HARD REQUIREMENT 2: USED_BY FIELD
In the used_by field, list ONLY the file names, not paths.
"""

def get_dependencies_user_prompt(
    files_listing: dict,
    partial_dependency_list: list,
    file_name: str,
    schema: SchemaCreator
) -> str:
    user_prompt = {
        "files_listing": files_listing,
        "partial_dependencies_list": partial_dependency_list,
        "file_name_to_identify_dependencies_for": file_name,
        "important_instructions": important_instructions
    }
    user_prompt = json.dumps(user_prompt, indent=4)
    if schema.validate(user_prompt):
        return user_prompt
    else:
        raise ValueError("User prompt does not conform to schema")
    
def normalize_file_names(dependencies: dict) -> dict:
    dependencies["used_by"] = [Path(user).name for user in dependencies["used_by"]]
    return dependencies

@retry(max_attempts=3, delay=1)
async def get_dependencies(
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
        validate_chat_response(response, get_dependencies_output_schema())
        response_dict = json.loads(response)
        if not response_dict["used_by"]:
            response_dict["used_by"] = []
        response_dict = normalize_file_names(response_dict)
        return response_dict
    except Exception as e:
        print(json.dumps(json.load(response), indent=4))
        print(f"Error in get_dependencies: {e}")
        raise e
    

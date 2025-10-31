from devteam.api_call_functionality.api_calls import get_chat_response
from devteam.schemas.schema_creation import *
from devteam.system_prompts.system_prompts import *
from devteam.helper_functionality.helpers import *
from devteam.config.config import *
from devteam.decorators.decorators import retry
import asyncio
import json
import copy

def get_class_generation_user_prompt(
    original_user_prompt: str,
    project_overview: str,
    files_listing: str,
    file_name: str,
    schema: SchemaCreator
) -> str:
    user_prompt = {
        "original_user_prompt": original_user_prompt,
        "project_overview": project_overview,
        "files_listing": files_listing,
        "file_name": file_name,
    }
    user_prompt = json.dumps(user_prompt, indent=4)
    if schema.validate(user_prompt):
        return user_prompt
    else:
        raise ValueError("User prompt does not conform to schema")
@retry(3,1)
async def get_class(
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
        validate_chat_response(response, get_class_generation_output_schema())
        response_dict = json.loads(response)
        return response_dict
    except Exception as e:
        print(response)
        print(f"Error in get_class: {e}")
        raise e


from devteam.api_call_functionality.api_calls import get_chat_response
from devteam.schemas.schema_creation import *
from devteam.system_prompts.system_prompts import *
from devteam.helper_functionality.helpers import *
from devteam.config.config import *
from devteam.decorators.decorators import retry
import asyncio


def get_responsibilities_user_prompt(
    project_overview: str,
    file_name: str,
    files_listing: str
) -> str:
    user_prompt = {
        "project_overview": project_overview,
        "files_listing": files_listing,
        "file_name": file_name,
    }
    return json.dumps(user_prompt)

@retry(max_attempts=3, delay=1)
async def get_responsibilities(
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
        validate_chat_response(response, get_responsibilities_output_schema())
        response_dict = json.loads(response)
        return response_dict
    except Exception as e:
        print(f"Error in get_responsibilities: {e}")
        raise e
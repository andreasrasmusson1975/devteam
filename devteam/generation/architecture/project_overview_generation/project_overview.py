from devteam.api_call_functionality.api_calls import get_chat_response
from devteam.schemas.schema_creation import *
from devteam.system_prompts.system_prompts import *
from devteam.helper_functionality.helpers import *
from devteam.decorators.decorators import retry
from devteam.config.config import *
import asyncio

confusing_initial_content_detected_init = "Please suggest a valid python project idea."
initial_project_overview_init = "Here's a project overview based on your suggestion."
initial_project_overview_ending = """
If you like, you can suggest changes to this project overview according to the rules outlined below.

[italic cyan]Allowed changes[/italic cyan]

- Adding more goals to the main goals section if they are compatible with existing goals.
- Adding more frameworks and technologies to the frameworks and technologies section if they are compatible with existing ones.
- Adding more security goals to the security goals section if they are compatible with existing ones.
- Changing the project name to a different name.
- Changing the project description in a way that is compatible with existing goals.

[italic cyan]Non-allowed changes[/italic cyan]

- Removing any goals from the main goals section.
- Removing any security goals from the security goals section.
- Changing the project description in a way that contradicts existing goals.
- Removing entire sections, for instance removing the "security goals" section.
- Changing the programming language to something other than python.

Please either accept this project overview or suggest changes according to the rules above.
"""
change_not_allowed = "The change you requested is not allowed."
improved_project_overview_init = "Here's the new and improved project overview based on your feedback."
improved_project_overview_ending = """
The project overview has been refined based on your input. 
Do you accept this version, or would you like to suggest further changes?
"""
accepted_project_overview_init = ""

bad_content_detected_init = """
The content of the user prompt has been deemed unsafe or inappropriate. 
This incident has been logged. Please provide a different prompt.
"""

confusing_project_overview_improvement_content_detected_init = """
Please either accept the existing project overview or provide clear and specific feedback on what you'd like to change.
"""

def get_initial_user_prompt(
    conversation_history: list, 
    user_prompt: str, 
    schema: SchemaCreator
) -> str:
    user_prompt = {
        "conversation_history": conversation_history,
        "user_prompt": user_prompt
    }
    user_prompt = json.dumps(user_prompt, indent=4)
    if schema.validate(user_prompt):
        return user_prompt
    else:
        raise ValueError("User prompt does not conform to schema")

@retry(max_attempts=3, delay=1)
def get_project_overview_improvement_user_prompt(
    original_project_overview: str,
    user_feedback: str,
    schema: SchemaCreator
) -> str:
    user_prompt = {
        "original_project_overview": original_project_overview,
        "user_feedback": user_feedback
    }
    user_prompt = json.dumps(user_prompt, indent=4)
    if schema.validate(user_prompt):
        return user_prompt
    else:
        raise ValueError("User prompt does not conform to schema")

async def get_user_prompt_classification(
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
        response = json.loads(response)
        response['category'] = int(response['category'])
        response['confidence'] = float(response['confidence'])
        response = json.dumps(response)
        validate_chat_response(response, get_user_prompt_classification_output_schema())
        return json.loads(response)
    except Exception as e:
        raise

async def get_initial_project_overview(user_prompt) -> tuple:
    try:
        response = await get_chat_response(
            system_prompt=POSP,
            user_prompt=user_prompt,
            which_model=1,
            model_name=model_name,
        )
        validate_chat_response(response, get_project_overview_output_schema())
        project_overview = json.loads(response)
        lines = []
        lines.append(initial_project_overview_init+"\n")
        lines.extend(project_overview_to_markdown(project_overview))
        lines.append(initial_project_overview_ending)
        return response, lines
    except Exception as e:
        raise

async def get_improved_project_overview(
        user_prompt: str,
) -> tuple: 
    try:
        response = await get_chat_response(
            system_prompt=POIP,
            user_prompt=user_prompt,
            which_model=1,
            model_name=model_name,
        )
        validate_chat_response(response, get_project_overview_output_schema())
        project_overview = json.loads(response)
        lines = []
        lines.append(improved_project_overview_init+"\n")
        lines.extend(project_overview_to_markdown(project_overview))
        lines.append(improved_project_overview_ending)
        return project_overview, lines
    except Exception as e:
        raise
    
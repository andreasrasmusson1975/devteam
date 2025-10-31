import json
import genson
from jsonschema import validate, ValidationError
from pathlib import Path
import joblib
class SchemaCreator:
    def __init__(
        self,
        **kwargs
    ):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def create_schema(self) -> dict:
        dict_representation = self.__dict__
        schema = genson.SchemaBuilder()
        schema.add_object(dict_representation)
        return schema.to_json(indent=4)

    def get_json(self) -> str:
        return json.dumps(self.__dict__, indent=4)
    
    def validate(self, json_data: str) -> bool:
        schema = self.create_schema()
        try:
            validate(instance=json.loads(json_data), schema=json.loads(schema))
            return True
        except ValidationError as e:
            raise

def get_user_prompt_input_schema() -> "SchemaCreator":   
    return SchemaCreator(
        conversation_history=[
            {
                "role": "string",
                "content": "string"
            }
        ],
        user_prompt="string",
    )

def get_user_prompt_classification_output_schema() -> "SchemaCreator":
    return SchemaCreator(
        category=1,
        confidence=0.7,
        explanation="string",
        warnings_about_content=["string"]
    )

def get_project_overview_output_schema() -> "SchemaCreator":
    return SchemaCreator(
        project_name="string",
        project_description="string",
        main_goals=["string"],
        frameworks_and_technologies=[
            {"name": "string", "description": "string", "reason for inclusion": "string"}
        ],
        security_goals=["string"],
        notes=["string"],
    )

def get_project_overview_improvement_input_schema() -> "SchemaCreator":
    return SchemaCreator(
        original_project_overview="string",
        user_feedback="string"
    )

def get_files_listing_input_schema() -> "SchemaCreator":
    return SchemaCreator(
        project_overview="string",
        instructions_for_output=[
            {
                "output_section_name": "string",
                "section_mandatory": True,
                "allowed_file_endings": ["string"],
                "instructions": ["string"] 
            }
        ]
    )

def get_files_listing_output_schema() -> "SchemaCreator":
    return SchemaCreator(
        environment_file={
            "file_name": "string",
            "file_description": "string",
        },
        readme_file={
            "file_name": "string",
            "file_description": "string",
        },
        entrypoint_file={
            "file_name": "string",
            "file_description": "string",
        },
        install_sh={
            "file_name": "string",
            "file_description": "string",
        },
        install_bat={
            "file_name": "string",
            "file_description": "string",
        },
        config_file={
            "file_name": "string",
            "file_description": "string",
        },
        pyproject_toml_file={
            "file_name": "string",
            "file_description": "string",
        },
        app_package={
            "package_name": "string",
            "files": [
                {
                    "file_name": "string",
                    "file_description": "string",
                    "dependencies": ["string"],
                    "corresponding_test_file_name": "string"
                }
            ]
        },
        core_folder=[
            {
                "file_name": "string",
                "file_description": "string"
            }
        ],
        services_folder=[
            {
                "file_name": "string",
                "file_description": "string"
            }
        ],
        models_folder=[
            {
                "file_name": "string",
                "file_description": "string"
            }
        ],
        utils_folder=[
            {
                "file_name": "string",
                "file_description": "string"
            }
        ],
        adapters_folder=[
            {
                "file_name": "string",
                "file_description": "string"
            }
        ],
        assets_folder=[
            {
                "file_name": "string",
                "file_description": "string"
            }
        ],
        static_folder={
            "js_files": [
                {
                    "file_name": "string",
                    "file_description": "string"
                }
            ],
            "css_files": [
                {
                    "file_name": "string",
                    "file_description": "string"
                }
            ]
        },
        templates_folder=[
            {
                "file_name": "string",
                "file_description": "string"
            }
        ],
        tests_folder=[
            {
                "file_name": "string",
                "file_description": "string",
                "tested_module": "string"
            }
        ],
        log_files=[
            {
                "file_name": "string",
                "file_description": "string"
            }
        ],
        documentation_files=[
            {
                "file_name": "string",
                "file_description": "string"
            }
        ],
        docker_files=[
            {
                "file_name": "string",
                "file_description": "string"
            }
        ],
        integration_summary="string",
    )



def get_improved_files_listing_input_schema() -> "SchemaCreator":
    return SchemaCreator(
        original_user_prompt="string",
        project_overview="string",
        generated_files_listing="string",
        instructions_for_output=[
            {
                "output_section_name": "string",
                "section_mandatory": True,
                "allowed_file_endings": ["string"],
                "instructions": ["string"]
            }
        ],
        task="string"
    )

def get_responsibilities_input_schema() -> "SchemaCreator":
    return SchemaCreator(
        project_overview="string",
        files_listing="string",
        file_name="string"
    )

def get_responsibilities_output_schema() -> "SchemaCreator":
    return SchemaCreator(
        file_name="string",
        responsibilities=["string"]
    )

def get_dependencies_input_schema() -> "SchemaCreator":
    file_path = Path(__file__).parent.parent / "assets" / "files_listing_for_dependencies.pkl"
    files = joblib.load(file_path)
    return SchemaCreator(
        files_listing=files,
        partial_dependencies_list=[
            {
                "file_name": "string",
                "used_by": ["string"]
            }
        ],
        file_name_to_identify_dependencies_for="string",
        important_instructions="string"
    )

def get_dependencies_output_schema() -> "SchemaCreator":
    return SchemaCreator(
        file_name="string",
        used_by=["string"]
    )

def get_class_generation_input_schema() -> "SchemaCreator":
    return SchemaCreator(
        original_user_prompt="string",
        project_overview="string",
        files_listing="string",
        file_name="string"
    )

def get_class_generation_output_schema() -> "SchemaCreator":
    return SchemaCreator(
        classes = [
            {
                "class_name": "string",
                "class_description": "string",
                "attributes": [
                    {
                        "attribute_name": "string",
                        "attribute_type": "string",
                        "attribute_description": "string"
                    }
                ],
                "methods": [
                    {
                        "method_name": "string",
                        "method_description": "string",
                        "parameters": [
                            {
                                "parameter_name": "string",
                                "parameter_type": "string",
                                "parameter_description": "string"
                            }
                        ],
                        "return_type": "string"
                    }
                ]
            }
        ],
        integration_summary="string"
    )

def get_js_function_generation_input_schema() -> "SchemaCreator":
    return SchemaCreator(
        original_user_prompt="string",
        project_overview="string",
        files_listing="string",
        file_name="string"
    )

def get_js_function_generation_output_schema() -> "SchemaCreator":
    return SchemaCreator(
        functions = [
            {
                "function_name": "string",
                "function_description": "string",
                "parameters": [
                    {
                        "parameter_name": "string",
                        "parameter_type": "string",
                        "parameter_description": "string"
                    }
                ],
                "return_type": "string"
            }
        ],
        integration_summary="string"
    )

def get_code_generation_input_schema() -> "SchemaCreator":
    path = Path(__file__).parent.parent / "assets" / "architecture_dict.pkl"
    architecture_dict = joblib.load(path)
    architecture_dict["file_to_implement"] = "string"
    architecture_dict["instructions"] = "string"
    return SchemaCreator(
        project_overview = architecture_dict["project_overview"],
        files_listing = architecture_dict["files_listing"],
        implementations_so_far =[{
            "file_name": "string",
            "content": "string"
        }],
        file_to_implement = architecture_dict["file_to_implement"],
        project_tree = "string", 
        instructions = architecture_dict["instructions"]
    )

def get_env_var_content_output_schema() -> "SchemaCreator":
    return SchemaCreator(
        file_name="string",
        content=[
            {
                "env_variable_name": "string",
                "description and purpose": "string",
                "example_value": "string"
            }
        ]
    )

def get_py_file_generation_output_schema() -> "SchemaCreator":
    return SchemaCreator(
        file_name="string",
        content="string"
    )

def get_js_file_generation_output_schema() -> "SchemaCreator":
    return SchemaCreator(
        file_name="string",
        content="string"
    )

def get_css_file_generation_output_schema() -> "SchemaCreator":
    return SchemaCreator(
        file_name="string",
        content="string"
    )

def get_md_file_generation_output_schema() -> "SchemaCreator":
    return SchemaCreator(
        file_name="string",
        content="string"
    )

def get_html_file_generation_output_schema() -> "SchemaCreator":
    return SchemaCreator(
        file_name="string",
        content="string"
    )

def get_docker_file_generation_output_schema() -> "SchemaCreator":
    return SchemaCreator(
        file_name="string",
        content="string"
    )

def get_requirements_in_generation_input_schema() -> "SchemaCreator":
    return SchemaCreator(
        files_listing=[{
            "file_name": "string",
            "content": "string"
        }]
    )

def get_requirements_in_generation_output_schema() -> "SchemaCreator":
    return SchemaCreator(
        requirements_in=[
            {
                "package_name": "string",
                "description": "string"
            }
        ]
    )

def get_install_file_generation_output_schema() -> "SchemaCreator":
    return SchemaCreator(
        install_file = {
            "file_name": "string",
            "content": "string"
        }
    )

def get_pyproject_toml_generation_output_schema() -> "SchemaCreator":
    return SchemaCreator(
        file_name="string",
        content="string"
    )

   




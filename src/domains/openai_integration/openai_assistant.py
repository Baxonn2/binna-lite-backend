from typing import List, TYPE_CHECKING
from openai.types.beta.assistant_tool_param import AssistantToolParam
from openai.types.beta.function_tool_param import FunctionToolParam
from openai.types.beta.assistant import Assistant
import json

# if TYPE_CHECKING:
#     from src.domains.openai_integration.openai_integration import openai

binna_instructions = """\
Eres un asistente llamada Binna. Estas enfocada a ayudar a todos los usuarios que requieran tu ayuda.
Tu misión es apoyar a el desarrollo y cierre de ventas B2B :D.
"""

type_parser_map = {
    'str': 'string',
    "int": "number",
    "float": "number",
    "bool": "boolean"
}


class FunctionParser:
    """
    Transform a function definition into a JSON schema object.
    """

    def __init__(self, function):
        annotations = function.__annotations__
        self.function_name = function.__name__
        self.function_description = function.__doc__
        self.function_return = annotations["return"]
        self.function_parameters = {
            "type": "object",
            "properties": {}
        }
        for param_name, param_type in annotations.items():
            if param_name == "return":
                continue
            if not isinstance(param_type, type):
                raise ValueError(
                    f"Invalid type for parameter {param_name} in function {self.function_name}"
                )
            self.function_parameters['properties'][param_name] = {
                "type": type_parser_map[param_type.__name__],
                "description": "Nombre del sujeto a saludar" # TODO: parse description from docstring
            }

        # self.function_parameters = {
        #     key: value for key, value in annotations.items() if key != "return"
        # }
    
    def __get_function_description(self):
        return {
            "name": self.function_name,
            "description": self.function_description,
            "parameters": self.function_parameters
        }
    
    def as_tool_param(self) -> FunctionToolParam:
        return {
            "type": "function",
            "function": self.__get_function_description()
        }
    
def hello_user(name: str) -> str:
    """
    Responde con un saludo personalizado.

    Args:
        name: Nombre del usuario a saludar.

    Returns:
        str: Retorna el mensaje de saludo personalizado
    """
    return f"Hola! {name} <3"

functions: List[AssistantToolParam] = [
    FunctionParser(hello_user).as_tool_param()
]


class BinnaAssistantDescription:
    model = "gpt-3.5-turbo-0125"
    name = "Binna Lite V0.0.1"
    description = "Una versión más ligera de Binna, con menos parámetros y menos capacidad de respuesta."
    instructions = binna_instructions
    tools: List[AssistantToolParam] = functions

    @classmethod
    def is_equal(cls, assistant: Assistant):
        is_same_model = assistant.model == cls.model
        is_same_name = assistant.name == cls.name
        is_same_description = assistant.description == cls.description
        is_same_instructions = assistant.instructions == cls.instructions

        assistant_tools_as_dicts = []
        for tool in assistant.tools:
            if tool.type == "function":
                assistant_tools_as_dicts.append({
                    "type": tool.type,
                    "function": {
                        "name": tool.function.name,
                        "description": tool.function.description,
                        "parameters": tool.function.parameters
                    }
                })
            else:
                raise NotImplementedError(f"Unknown tool type: {tool.type}")
        
        is_same_tools = json.dumps(
            assistant_tools_as_dicts,
            sort_keys=True
        ) == json.dumps(
            cls.tools,
            sort_keys=True
        )

        comparison_results = {
            "is_same_model": is_same_model,
            "is_same_name": is_same_name,
            "is_same_description": is_same_description,
            "is_same_instructions": is_same_instructions,
            "is_same_tools": is_same_tools
        }

        for key, value in comparison_results.items():
            if not value:
                print(f"{key}: {value}")

        return all(comparison_results.values())


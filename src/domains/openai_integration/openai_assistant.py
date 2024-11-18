from typing import List, TYPE_CHECKING, Optional, TypeVar, get_origin, get_args, Union
from src.domains.openai_integration import IgnoreMe
from src.domains.customer.controller import EstablishmentController
from openai.types.beta.assistant_tool_param import AssistantToolParam
from openai.types.beta.function_tool_param import FunctionToolParam
from openai.types.beta.assistant import Assistant
import json


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

def check_is_optional(field):
    return get_origin(field) is Union and \
        type(None) in get_args(field)

def check_is_ignored(field):
    return get_origin(field) is Union and \
        IgnoreMe in get_args(field)


class FunctionParser:
    """
    Transform a function definition into a JSON schema object.
    """

    def __init__(self, function):
        self.function_name = function.__name__

        annotations = function.__annotations__
    
        parsed_docstring = self.__parse_docstring(function)
        self.function_description = parsed_docstring["description"]
        self.function_parameters = {
            "type": "object",
            "properties": {},
        }


        self.strict_mode = True
        required_properties = []
        for param_name, param_type in annotations.items():
            if param_name == "return":
                continue
            
            # Si es un Optional, entonces no es requerido
            is_optional = False
            param_type_name = param_type.__name__
            if check_is_optional(param_type):
                is_optional = True
                self.strict_mode = False
                param_type_name = get_args(param_type)[0].__name__
            elif check_is_ignored(param_type):
                continue

            elif not isinstance(param_type, type):
                raise ValueError(
                    f"Invalid type for parameter {param_name} in function {self.function_name}"
                )
            self.function_parameters['properties'][param_name] = {
                "type": type_parser_map[param_type_name],
                "description": parsed_docstring["args"].get(param_name, ""),
            }

            if not is_optional:
                required_properties.append(param_name)

        self.function_parameters["required"] = required_properties
        if self.strict_mode:
            self.function_parameters["additionalProperties"] = False          
    
    def __get_function_description(self):

        return {
            "name": self.function_name,
            "description": self.function_description,
            "parameters": self.function_parameters,
            "strict": self.strict_mode,
        }
    
    def __parse_docstring(self, function):
        import re

        docstring = function.__doc__
        if not docstring:
            raise ValueError(f"Function {function.__name__} has no docstring")
        
        # Docstring sections
        description_match = re.search(r'^\s*(.*?)(?=\n\s*\n|Args:|Returns:)', docstring, re.DOTALL)
        print("description_match", description_match)
        description = description_match.group(1).strip() if description_match else None
        print("description", description)

        # Extract Args
        args_section_match = re.search(r"Args:\n((?:\s+- .*?\n)+)", docstring)
        if args_section_match:
            args_section = args_section_match.group(1)
            arg_pattern = r"^\s*-\s+(\w+):\s*(.*)$"
            matches = re.findall(arg_pattern, args_section, re.MULTILINE)
            args = {arg: description for arg, description in matches}
        else:
            args = {}
        
        # Extract Returns
        returns_section = re.search(r'Returns:\n((?:\s+- .*?\n)+)', docstring)
        returns = None
        if returns_section:
            return_type, return_description = returns_section.group(1).strip().split(": ", 1)
            return_type = return_type.strip().split("- ", 1)[1]
            returns = {
                "type": return_type,
                "description": return_description
            }

        return_to_description = f"Recibirás como respuesta {returns['description']}" if returns else None
        if return_to_description:
            description = f"{description}\n\n{return_to_description}"

        return {
            "description": description,
            "args": args,
            "returns": returns,
        }
    
    def as_tool_param(self) -> FunctionToolParam:
        return {
            "type": "function",
            "function": self.__get_function_description(),
        }
    
def hello_user(name: str) -> str:
    """
    Responde con un saludo personalizado.

    Args:
    - name: Nombre del usuario a saludar.

    Returns:
    - str: un mensaje de saludo personalizado
    """
    return f"Hola! {name} <3"

def add_customer(name: str, email: str, phone: str, age: Optional[int]) -> str:
    """
    Añade un nuevo cliente a la base de datos.

    Args:
    - name: Nombre del cliente.
    - email: Correo del cliente.
    - phone: Teléfono del cliente.
    - age: Edad del cliente.

    Returns:
    - str: Mensaje de confirmación.
    """
    return f"Cliente {name} añadido correctamente."

functions: List[AssistantToolParam] = [
    FunctionParser(add_customer).as_tool_param(),
    FunctionParser(hello_user).as_tool_param(),
    FunctionParser(EstablishmentController.create_customer).as_tool_param(),
    FunctionParser(EstablishmentController.get_all_customer).as_tool_param(),
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
                    "function": tool.function.to_dict()
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


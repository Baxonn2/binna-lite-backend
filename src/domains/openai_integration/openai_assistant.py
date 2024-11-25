import inspect
from typing import List, get_origin, get_args, Union
from src.domains.openai_integration import IgnoreMe, DateTimeStringClass
from src.domains.customer.controllers.additional_note_controller import AdditionalNoteController
from src.domains.customer.controllers.establishment_controller import EstablishmentController
from src.domains.customer.controllers.contact_controller import ContactController
from src.domains.customer.controllers.task_controller import TaskController
from src.domains.customer.controllers.opportunity_controller import OpportunityController
from openai.types.beta.assistant_tool_param import AssistantToolParam
from openai.types.beta.function_tool_param import FunctionToolParam
from openai.types.beta.assistant import Assistant
from openai.types.chat_model import ChatModel
import json


binna_instructions = """\
Eres un asistente llamada Binna. Estas enfocada a ayudar a todos los usuarios que requieran tu ayuda.
Tu misión es apoyar a el desarrollo y cierre de ventas B2B.
"""

type_parser_map = {
    'str': 'string',
    "int": "number",
    "float": "number",
    "bool": "boolean",
    "datetime": "string",
}

type_regex_map = {
    "datetime": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$"
}

def check_is_optional(field):
    return get_origin(field) is Union and \
        type(None) in get_args(field)

def check_is_ignored(field):
    return get_origin(field) is Union and \
        IgnoreMe in get_args(field)

def check_is_datetime_string(field):
    return get_origin(field) is Union and \
        DateTimeStringClass in get_args(field)


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
                param_type = get_args(param_type)[0]
            elif check_is_ignored(param_type):
                continue

            elif not isinstance(param_type, type):
                raise ValueError(
                    f"Invalid type for parameter {param_name} in function {self.function_name}"
                )
            
            if check_is_datetime_string(param_type):
                param_type_name = "datetime"

            self.function_parameters['properties'][param_name] = {
                "type": type_parser_map[param_type_name],
                "description": parsed_docstring["args"].get(param_name, ""),
            }

            # Adding pattern for specific types
            if type_regex_map.get(param_type_name):
                self.function_parameters['properties'][param_name]["pattern"] = type_regex_map[param_type_name]

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
        description = description_match.group(1).strip() if description_match else None

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
    

# Map the function names to the actual functions
function_name_map = {
    # Customer Establishment methods
    "create_customer": EstablishmentController.create_customer,
    "get_all_customer": EstablishmentController.get_all_customer,
    "get_customer_by_id": EstablishmentController.get_customer_by_id,
    "update_customer": EstablishmentController.update_customer,
    "delete_customer": EstablishmentController.delete_customer,
    "get_customer_by_name": EstablishmentController.get_customer_by_name,   

    # Additional Note methods
    "create_additional_note": AdditionalNoteController.create_additional_note,
    "get_all_additional_notes": AdditionalNoteController.get_all_additional_notes,
    "get_all_additional_notes_summarized": AdditionalNoteController.get_all_additional_notes_summarized,
    "get_additional_note": AdditionalNoteController.get_additional_note,
    "update_additional_note": AdditionalNoteController.update_additional_note,
    "delete_additional_note": AdditionalNoteController.delete_additional_note,

    # Contact methods
    "create_contact": ContactController.create_contact,
    "get_all_contacts": ContactController.get_all_contacts,
    "get_contact": ContactController.get_contact,
    "update_contact": ContactController.update_contact,
    "delete_contact": ContactController.delete_contact,

    # Task methods
    "create_task": TaskController.create_task,
    "get_all_tasks": TaskController.get_all_tasks,
    "update_task": TaskController.update_task,
    "delete_task": TaskController.delete_task,

    # Opportunity methods
    "create_opportunity": OpportunityController.create_opportunity,
    "get_all_opportunities": OpportunityController.get_all_opportunities,
    "get_opportunity_by_id": OpportunityController.get_opportunity_by_id,
    "update_opportunity": OpportunityController.update_opportunity,
    "delete_opportunity": OpportunityController.delete_opportunity,
}

# Functions to be used as tools
# DocStrings are used to generate the description of the tool.
functions = [ FunctionParser(func).as_tool_param() for func in function_name_map.values() ]


class BinnaAssistantDescription:
    model: ChatModel = "gpt-4o-mini"
    name = "Binna Lite V0.0.2"
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

    @classmethod
    def call_function_tool(cls, function_name: str, **kwargs):
        if function_name in function_name_map:
            function_to_call = function_name_map[function_name]
            
            signature = inspect.signature(function_to_call)
            expected_params = signature.parameters.keys()

            filtered_args = {k: v for k, v in kwargs.items() if k in expected_params}

            return function_to_call(**filtered_args)
        else:
            raise ValueError(f"Function {function_name} not found in tools")

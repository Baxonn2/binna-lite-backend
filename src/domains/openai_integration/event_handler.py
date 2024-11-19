from typing import Optional, TypedDict
from openai import OpenAI, AssistantEventHandler
from openai.types.beta.threads import Text
from sqlmodel import Session, select
from typing_extensions import override
import json
from src.domains.openai_integration.openai_assistant import BinnaAssistantDescription
from src.domains.auth.models.user import User


DetailItem = TypedDict("DetailItem", {"title": str, "subtitle": str, "icon": str})

class CRUDActionHandler:
    def __init__(self, db: Session, controller):
        self.db = db
        self.controller = controller

class EventHandler(AssistantEventHandler):
    tool_outputs = None
    executing_tool = False

    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        super().__init__()

    @override
    def on_text_created(self, text) -> None:
        print(f"\ngenerating new binna response ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)
    
    @override
    def on_text_done(self, text: Text) -> None:
        print(f"\n\n")

    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == "code_interpreter":
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)

    @override
    def on_event(self, event):
        """
        Retrieve events thats are denoted with 'requires_action'
        since these will have our tool_calls

        Args:
            event (_type_): _description_
        """
        if event.event == "thread.run.requires_action":
            run_id = event.data.id
            self.handle_requires_action(event.data, run_id)

    def __make_tool_output(
        self,
        tool_call_id: str,
        success: bool,
        function_name: str,
        message: str,
        detail_list: Optional[list[DetailItem]] = None,
        **kwargs
    ):
        """
        Create a tool output

        Args:
            tool_call_id (str): id of the tool call. This id is used to identify the tool call
            success (bool): a boolean value that indicates if the tool call was successful
            function_name (str): the name of the function that was executed. Don't use code function name
            message (str): a message that describes the result of the tool call
            detail_list (Optional[list]): a list of dictionaries that contains the details of the tool call

        Returns:
            _type_: _description_
        """
        output = {
            success: success,
            function_name: function_name,
            message: message,
        }
        if detail_list:
            output["detail_list"] = detail_list
        output.update(kwargs) # type: ignore

        return {
            "tool_call_id": tool_call_id,
            "output": json.dumps(output, default=str)
        }
    
    def handle_requires_action(self, data, run_id):
        """
        Handle the requires action event

        Args:
            data (_type_): _description_
            run_id (_type_): _description_
        """
        self.executing_tool = True
        tool_outputs = []

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            print(f"Tool call (user_id: {self.user.id}): {tool.function.name}")

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            arguments = json.loads(tool.function.arguments)
            automatic_registered_tool_output = BinnaAssistantDescription.call_function_tool(
                function_name=tool.function.name,
                db=self.db,
                user_id=self.user.id,
                **arguments
            )
            tool_outputs.append(self.__make_tool_output(
                tool_call_id=tool.id,
                success=automatic_registered_tool_output is not None,
                function_name=tool.function.name,
                message="Successfully executed tool",
                output=automatic_registered_tool_output
            ))

            # if tool.function.name == "get_saved_customers":
            #     tool_outputs.append(self.__make_tool_output(
            #         tool_call_id=tool.id,
            #         success=True,
            #         function_name="Obtener clientes",
            #         message="Clientes recuperados exitosamente",
            #         customers=['Cliente de prueba 1', 'Cliente de prueba 2']
            #     ))
            

        self.tool_outputs = tool_outputs
        self.executing_tool = False

        
from openai import OpenAI, AssistantEventHandler
from typing_extensions import override
import json
from src.domains.openai_integration.openai_integration import OPENAI_API_KEY, OPENAI_ASSISTANT_KEY

# Create an instance of the OpenAI class
openai = OpenAI(api_key=OPENAI_API_KEY)
thread = openai.beta.threads.create()
assistant = openai.beta.assistants.retrieve(OPENAI_ASSISTANT_KEY or "NOT_FOUND")

class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

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

    def handle_requires_action(self, data, run_id):
        """
        Handle the requires action event

        Args:
            data (_type_): _description_
            run_id (_type_): _description_
        """
        tool_outputs = []

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "add_new_customer":
                arguments = json.loads(tool.function.arguments)
                company_name = arguments.get("company_name")
                company_description = arguments.get("company_description")
                
                # TODO: add here the logic to save the new customer
                tool_outputs.append(
                    {
                        "tool_call_id": tool.id,
                        "output": json.dumps({
                            "success": True,
                            "new_customer": {
                                "company_name": company_name,
                                "company_description": company_description
                            }
                        })
                    }
                )

        self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        """
        Submit the tool outputs

        Args:
            tool_outputs (_type_): _description_
            run_id (_type_): _description_
        """
        with openai.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=self.current_run.id,
            tool_outputs=tool_outputs,
            event_handler=EventHandler(),
        ) as stream:
            stream.until_done()



# Create a new assistant session
while True:
    # Loop to keep the assistant running
    user_input = input("\nYou > ")
    if user_input == "exit":
        break
    new_message = openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )
    with openai.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        event_handler=EventHandler()
    ) as stream:
        stream.until_done()


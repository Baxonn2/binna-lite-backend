from typing import Optional

from sqlmodel import Session
from src.domains.auth.models.user import User
from src.domains.auth.models.user_usage import UserUsage
from src.domains.openai_integration.openai_integration import openai, assistant
from src.domains.openai_integration.event_handler import EventHandler
from openai.types.beta.threads.run import Usage
from datetime import datetime
import json

class ThreadManager:

    def __init__(self, thread_id: Optional[str], db: Session, user: User):
        if thread_id:
            print("Retrieving existing thread", thread_id)
            self.thread = openai.beta.threads.retrieve(thread_id)
        else:
            print("Creating new thread")
            self.thread = openai.beta.threads.create()

        self.db = db
        self.user = user

    def retrieve_messages(self):
        """
        Retrieve the messages of the assistant
        """
        messages = openai.beta.threads.messages.list(thread_id=self.thread.id)
        return messages

    def stream_response(self, input_message: Optional[str] = None, tool_outputs: list[dict] = []):
        """
        Stream the response of the assistant

        Args:
            input_message (str): The message to send to the assistant
        """
        # Create a new message
        if input_message:
            openai.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=input_message
            )

        event_handler = EventHandler(self.db, self.user)

        # Stream result assistant response
        with openai.beta.threads.runs.stream(
            thread_id=self.thread.id,
            assistant_id=assistant.id,
            event_handler=event_handler,
            additional_instructions= "contexto: " + json.dumps(self.get_context_data())
        ) as stream:
            yield from stream.text_deltas
            stream.until_done()

        # Streaming tool outputs if exists
        if event_handler.tool_outputs:
            yield from self.stream_tool_outputs(
                event_handler.current_run.id,
                event_handler.tool_outputs
            )

        run_usage = openai.beta.threads.runs.retrieve(
            thread_id=self.thread.id,
            run_id=event_handler.current_run.id
        ).usage
        
        self.__save_usage(run_usage)

    def stream_tool_outputs(self, run_id: str, tool_outputs: list[dict]):
        """
        Stream the tool outputs of the assistant

        Args:
            tool_outputs (list[dict]): The tool outputs to send to the assistant
        """
        event_handler = EventHandler(self.db, self.user)

        with openai.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.thread.id,
            run_id=run_id,
            tool_outputs=tool_outputs,
            event_handler=event_handler
        ) as stream:
            yield from stream.text_deltas
            stream.until_done()

        if event_handler.tool_outputs:
            yield from self.stream_tool_outputs(
                run_id,
                event_handler.tool_outputs
            )
        
        yield "\json" + json.dumps(event_handler.tool_outputs)

    def get_context_data(self):
        context = {
            "current_datetime": datetime.now().isoformat(),
            "current_day": datetime.now().strftime("%A"),
        }

        if self.user.first_name:
            context["user_first_name"] = self.user.first_name
        
        if self.user.my_business_description:
            context["user_business_description"] = self.user.my_business_description

        print("Context data", context)
        return context

    def __save_usage(self, usage: Usage):
        """
        Save the usage of the assistant

        Args:
            usage (Usage): token usage of the assistant
        """
        cached_tokens = usage.model_dump().get(
            "prompt_tokens_detail", {}
        ).get("cached_tokens", 0)

        from src.domains.auth.controllers.user_usage_controller import UserUsageController

        UserUsageController.registry_usage(
            self.db,
            self.user.id,
            total_tokens=usage.total_tokens,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            cached_tokens=cached_tokens
        )
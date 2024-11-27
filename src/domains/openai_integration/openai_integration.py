from openai import OpenAI
from src.utils.settings import OPENAI_API_KEY, OPENAI_ASSISTANT_KEY

# Create an instance of the OpenAI class
openai = OpenAI(api_key=OPENAI_API_KEY)

from src.domains.openai_integration.openai_assistant import BinnaAssistantDescription

if not OPENAI_ASSISTANT_KEY:
    # Print an error message
    print("OPENAI_ASSISTANT_KEY is not set")
    raise Exception("OPENAI_ASSISTANT_KEY is not set")
else:
    # Retrieve the assistant
    assistant = openai.beta.assistants.retrieve(OPENAI_ASSISTANT_KEY)

    if not BinnaAssistantDescription.is_equal(assistant):
        print("Binna Config is not equal. Updating Binna assistant config")
        my_updated_assistant = openai.beta.assistants.update(
            OPENAI_ASSISTANT_KEY,
            description=BinnaAssistantDescription.description,
            name=BinnaAssistantDescription.name,

            instructions=BinnaAssistantDescription.instructions,
            model=BinnaAssistantDescription.model,
            tools=BinnaAssistantDescription.tools,
            temperature=BinnaAssistantDescription.temperature
        )
        assistant = my_updated_assistant
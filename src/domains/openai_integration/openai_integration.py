from openai import OpenAI
from src.utils.settings import OPENAI_API_KEY, OPENAI_ASSISTANT_KEY

# Create an instance of the OpenAI class
openai = OpenAI(api_key=OPENAI_API_KEY)

if not OPENAI_ASSISTANT_KEY:
    # Print an error message
    print("OPENAI_ASSISTANT_KEY is not set")
    raise Exception("OPENAI_ASSISTANT_KEY is not set")
else:
    # Retrieve the assistant
    assistant = openai.beta.assistants.retrieve(OPENAI_ASSISTANT_KEY)
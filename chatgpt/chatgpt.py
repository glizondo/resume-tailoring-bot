from openai import OpenAI
import credentials.credentials

client = OpenAI(
    # This is the default and can be omitted
    api_key=credentials.credentials.api_key,
)
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "What do you think about global warming?",
        }
    ],
    model="gpt-3.5-turbo",
)

print(chat_completion)

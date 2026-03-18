import os

import anthropic
import requests
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

client = anthropic.Anthropic()


def query_bedrock_api(query: str) -> str:
    api_url = os.environ["BEDROCK_API_URL"]
    response = requests.post(api_url, json={"query": query})
    response.raise_for_status()
    raw = response.json()["generated_response"]
    if "\n\nResponse: " in raw:
        raw = raw.split("\n\nResponse: ", 1)[1]
    return raw


def ask_assistant(user_input: str) -> str:
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        system="You are a concise assistant. Keep your answers short and to the point.",
        messages=[{"role": "user", "content": user_input}],
    )
    return response.content[0].text


if __name__ == "__main__":
    input = "How many levels has the game?"
    print(query_bedrock_api(input))

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import os
from config import short_name
import dotenv
from bot.setup.init import openai_sessions
dotenv.load_dotenv()

mistral_api_key = os.environ["MISTRAL_API_KEY"]
mistral_model = "mistral-medium"
mistral_client = MistralClient(api_key=mistral_api_key)

dont_explain = f" - Do not provide the rationale for your response. It should feel like a natural response from {short_name} to the previous message."
dont_tag = " - Do not beging your response by tagging the person you are replying to. They already know you are replying to them."
single_reponse = " - Only provide a single response, a single message. Do not split it into multiple messages."
dontoverdoweezer = " - Don't overdo the Weezer references. These are long time fans who are ready to talk about something else."
emoji = " - You can use emoji, but don't overdo it. Be very sparing. You are not a teenager."


def fetch_mistral_completion(message, system: str):
    print("fetch_mistral_completion")
    system += dontoverdoweezer + dont_explain + dont_tag + single_reponse + emoji
    # The first message is the system information and needs to be added every time
    # because you don't save it in the session
    messages = [
        ChatMessage(role="system", content=system),
    ]

    # Add the user's text to the openai session for this channel
    openai_sessions[message.channel.id].append(
        ChatMessage(role="user", content=f"{message.author.nick}: {message.clean_content}"))

    # Limit the number of messages in the session to 6
    if len(openai_sessions[message.channel.id]) > 6:

        openai_sessions[message.channel.id] = openai_sessions[message.channel.id][-3:]

    # add all the messages from this channel to the system message
    messages.extend(openai_sessions[message.channel.id])
    # print(f"messages: {messages}")
    for m in messages:
        print(m)

    # No streaming
    reply = mistral_client.chat(
        model=mistral_model,
        messages=messages,

    )

    text = reply.choices[0].message.content

    # add the response to the session. I suppose now there may be up to 7 messages in the session

    openai_sessions[message.channel.id].append(
        ChatMessage(role="assistant", content=text))

    return text

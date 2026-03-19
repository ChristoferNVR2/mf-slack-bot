import json
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import App
from dotenv import find_dotenv, load_dotenv
from flask import Flask, request

from functions import ask_assistant, query_bedrock_api

load_dotenv(find_dotenv())

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_USER_ID = os.environ["SLACK_BOT_USER_ID"]

app = App(token=SLACK_BOT_TOKEN)
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


def get_bot_user_id():
    try:
        slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        response = slack_client.auth_test()
        return response["user_id"]
    except SlackApiError as e:
        print(f"Error: {e}")


@app.event("app_mention")
def handle_mentions(body, say):
    text = body["event"]["text"]

    mention = f"<@{SLACK_BOT_USER_ID}>"
    text = text.replace(mention, "").strip()

    say("Sure, I'll get right on that!")
    # response = ask_assistant(text)
    response = query_bedrock_api(text)
    say(blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": response}}], text=response)


def ack_dm_message(ack):
    ack()


def process_dm_message(body, client, logger):
    event = body.get("event", {})
    if event.get("channel_type") != "im":
        return
    if event.get("subtype") or event.get("bot_id"):
        return

    query = event.get("text", "").strip()
    if not query:
        return

    channel_id = event["channel"]
    response = query_bedrock_api(query)
    try:
        client.chat_postMessage(
            channel=channel_id,
            blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": response}}],
            text=response,
        )
    except SlackApiError as e:
        logger.error(f"Error sending DM response: {e}")


app.event("message")(ack=ack_dm_message, lazy=[process_dm_message])


def ack_ask_privately(ack):
    ack()


def process_ask_privately(body, client, respond, logger):
    query = body.get("text", "").strip()
    if not query:
        respond(response_type="ephemeral", text="Please provide a question. Usage: `/ask-privately <your question>`")
        return
    user_id = body["user_id"]
    response = query_bedrock_api(query)
    try:
        dm = client.conversations_open(users=user_id)
        client.chat_postMessage(
            channel=dm["channel"]["id"],
            blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": response}}],
            text=response,
        )
    except SlackApiError as e:
        logger.error(f"Error sending private response: {e}")


app.command("/ask-privately")(ack=ack_ask_privately, lazy=[process_ask_privately])


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


@flask_app.route("/slack/ask-privately", methods=["POST"])
def ask_privately():
    return handler.handle(request)


if __name__ == "__main__":
    flask_app.run()

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import App
from dotenv import find_dotenv, load_dotenv
from flask import Flask, request

from functions import query_bedrock_api

load_dotenv(find_dotenv())

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]

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


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


if __name__ == "__main__":
    flask_app.run()

import os
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import App
from dotenv import find_dotenv, load_dotenv
from flask import Flask, request

from functions import query_bedrock_api

load_dotenv(find_dotenv())

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
ALLOWED_USER_IDS = set(os.environ.get("ALLOWED_SLACK_USER_IDS", "").split(","))

app = App(token=SLACK_BOT_TOKEN)
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


def ack_dm_message(ack):
    ack()


def process_dm_message(body, client, logger):
    event = body.get("event", {})
    if event.get("channel_type") != "im":
        return
    if event.get("subtype") or event.get("bot_id"):
        return

    user_id = event.get("user")
    if ALLOWED_USER_IDS and user_id not in ALLOWED_USER_IDS:
        # To reply instead: client.chat_postMessage(channel=event["channel"], text="You don't have access to this bot.")
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

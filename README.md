# mf-slack-bot

A Slack bot that answers questions by routing them to an AWS Bedrock API (or Claude directly as a fallback). It supports both channel mentions and a `/ask-privately` slash command that responds via DM.

## Features

- **`@mention`** — mention the bot in any channel to ask a question; it responds in the same channel.
- **`/ask-privately`** — slash command that sends the response to your DMs, keeping the query private.
- Powered by an **AWS Bedrock** API endpoint, with an optional **Anthropic Claude** fallback (`ask_assistant`).

## Tech stack

| Layer | Library |
|---|---|
| Slack integration | `slack-bolt`, `slack-sdk` |
| Web server | `Flask` |
| AI backend | AWS Bedrock (via REST) + `anthropic` SDK |
| Dependency management | `uv` |

## Setup

### 1. Prerequisites

- Python 3.14+
- [`uv`](https://github.com/astral-sh/uv) package manager
- A Slack app with:
  - **Bot token scopes:** `chat:write`, `im:write`, `commands`
  - **Event subscriptions:** `app_mention`
  - **Slash command:** `/ask-privately`
- An AWS Bedrock API endpoint (API Gateway URL)
- An Anthropic API key (for the direct Claude fallback)

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `SLACK_BOT_TOKEN` | Slack bot OAuth token (`xoxb-...`) |
| `SLACK_SIGNING_SECRET` | Slack app signing secret |
| `SLACK_BOT_USER_ID` | The bot's Slack user ID |
| `ANTHROPIC_API_KEY` | Anthropic API key (for direct Claude calls) |
| `BEDROCK_API_URL` | AWS API Gateway URL for your Bedrock endpoint |

### 4. Run the app

```bash
uv run python app.py
```

The Flask server starts on `http://localhost:5000` by default.

### 5. Expose locally for development

Use [ngrok](https://ngrok.com/) or a similar tunneling tool to expose the local server to Slack:

```bash
ngrok http 5000
```

Then configure the Slack app with:
- **Event subscription URL:** `https://<your-ngrok-url>/slack/events`
- **Slash command URL:** `https://<your-ngrok-url>/slack/ask-privately`

## Project structure

```
mf_slack_bot/
├── app.py          # Slack Bolt app, Flask routes, event/command handlers
├── functions.py    # AI backend calls (Bedrock API, Claude fallback)
├── pyproject.toml  # Project metadata and dependencies
├── uv.lock         # Locked dependency versions
└── .env.example    # Environment variable template
```

## Deployment

For production, run behind a WSGI server such as `gunicorn`:

```bash
uv run gunicorn app:flask_app
```

Make sure your deployment environment has all the required environment variables set.

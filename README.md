# mf-slack-bot

A Slack bot that answers questions by routing them to an AWS Bedrock API. Accessible exclusively via direct messages (DMs).

## Features

- **DM-only** — send the bot a direct message to ask a question; it replies in the same DM conversation.
- Powered by an **AWS Bedrock** API endpoint.

## Tech stack

| Layer | Library |
|---|---|
| Slack integration | `slack-bolt`, `slack-sdk` |
| Web server | `Flask` |
| AI backend | AWS Bedrock (via REST) |
| Dependency management | `uv` |

## Slack app setup (non-technical guide)

Follow these steps to create and configure the Slack app before running the bot.

### 1. Create the app

1. Go to [api.slack.com/apps](https://api.slack.com/apps) and click **Create New App**.
2. Choose **From scratch**, give it a name (e.g. `mf-slack-bot`), and select your workspace.

### 2. Grant permissions

1. In the left sidebar, go to **OAuth & Permissions**.
2. Scroll down to **Bot Token Scopes** and add the following scopes:
   - `chat:write` — allows the bot to send messages
   - `im:history` — allows the bot to read DM history
   - `im:read` — allows the bot to see DM conversations
   - `im:write` — allows the bot to open DM conversations

### 3. Enable event subscriptions

1. In the left sidebar, go to **Event Subscriptions** and toggle it **On**.
2. In the **Request URL** field, enter your server URL followed by `/slack/events` (e.g. `https://your-server.com/slack/events`). Slack will send a verification request — the bot must be running for this to succeed.
3. Under **Subscribe to bot events**, click **Add Bot User Event** and add:
   - `message.im` — triggers when someone sends the bot a DM

### 4. Enable the Messages tab

1. In the left sidebar, go to **App Home**.
2. Scroll down to **Show Tabs** and turn on **Messages Tab** (it is off by default).

This allows users to open a DM conversation with the bot directly from its profile.

### 5. Install the app to your workspace

1. In the left sidebar, go to **OAuth & Permissions**.
2. Click **Install to Workspace** and authorize the app.
3. Copy the **Bot User OAuth Token** (starts with `xoxb-`) — this is your `SLACK_BOT_TOKEN`.

### 6. Collect your credentials

| Where to find it | Used for |
|---|---|
| **OAuth & Permissions** → Bot User OAuth Token | `SLACK_BOT_TOKEN` |
| **Basic Information** → Signing Secret | `SLACK_SIGNING_SECRET` |
| **Basic Information** → App ID (or run `auth.test`) | `SLACK_BOT_USER_ID` |

---

## Setup

### 1. Prerequisites

- Python 3.14+
- [`uv`](https://github.com/astral-sh/uv) package manager
- A Slack app with:
  - **Bot token scopes:** `chat:write`, `im:history`, `im:read`, `im:write`
  - **Event subscriptions:** `message.im`
- An AWS Bedrock API endpoint (API Gateway URL)

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

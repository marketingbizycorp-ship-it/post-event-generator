# 🎙️ SpeakUp — Soft Skills & Professional Speaking Trainer

> A browser-based app to improve your professional English speaking and
> workplace soft skills. Practise speaking aloud, build professional
> vocabulary, and role-play real conversations — with instant, rule-based
> feedback. Runs fully offline, no API key needed.
>
> **➡️ See [`web/README.md`](web/README.md) for full docs and how to run it.**
>
> Quick start:
> ```bash
> cd web && python3 -m http.server 8000   # then open http://localhost:8000
> ```

---

# Slack Huddle Notes Bot

Automatically captures and summarizes Slack huddle notes when a huddle ends - no manual input required.

## Features

- Listens for huddle completion events via Slack Events API
- Automatically fetches huddle transcripts
- Generates AI-powered summaries using Claude or OpenAI
- Extracts action items with assignees
- Posts structured notes back to the channel

## Setup

### 1. Create a Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name it "Huddle Notes Bot" and select your workspace

### 2. Configure App Permissions

In your app settings:

**OAuth & Permissions** → Add these Bot Token Scopes:
- `channels:history` - Read channel messages
- `channels:read` - View basic channel info
- `chat:write` - Send messages
- `files:read` - Access files (transcripts)
- `users:read` - View user info

**Event Subscriptions** → Enable and subscribe to:
- `huddle_transcript_ready` - When transcript is available
- `message.channels` - Channel messages (for DM huddles)

**Socket Mode** → Enable Socket Mode (generates App Token)

### 3. Install to Workspace

1. Go to "Install App" in sidebar
2. Click "Install to Workspace"
3. Authorize the requested permissions
4. Copy the Bot User OAuth Token (`xoxb-...`)

### 4. Get Your Tokens

You'll need:
- **Bot Token** (`xoxb-...`): OAuth & Permissions page
- **App Token** (`xapp-...`): Basic Information → App-Level Tokens (create one with `connections:write` scope)
- **Signing Secret**: Basic Information → App Credentials

### 5. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your tokens:
```
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret

# For AI summaries (choose one)
ANTHROPIC_API_KEY=sk-ant-your-key
# OR
OPENAI_API_KEY=sk-your-key
```

### 6. Run the Bot

```bash
pip install -r requirements.txt
python main.py
```

The bot will now automatically generate notes when any huddle ends in channels it has access to.

## How It Works

1. **Huddle Ends** → Slack sends `huddle_transcript_ready` event
2. **Fetch Transcript** → Bot downloads the transcript file
3. **Process** → Parses speakers, timestamps, and content
4. **Generate Notes** → AI creates summary, key points, action items
5. **Post** → Structured notes posted to the channel

## Example Output

```
📝 Huddle Notes

Summary:
Team discussed Q2 roadmap priorities. Agreed to focus on mobile app 
improvements and defer API v2 until Q3.

Key Points:
• Mobile performance is the top priority
• Need to hire 2 more frontend engineers
• Beta launch targeted for June 15

Action Items:
• Draft mobile performance requirements (@sarah)
• Post job listings by Friday (@mike)
• Schedule customer interviews (@jen)

Decisions Made:
• API v2 moved to Q3
• Will use React Native for mobile
```

## Requirements

- Python 3.10+
- Slack workspace with Huddles enabled
- Slack Pro/Business+ plan (for huddle transcripts)

## Note on Huddle Transcripts

Slack huddle transcripts require:
- **Slack Pro, Business+, or Enterprise Grid** plan
- Transcription enabled in workspace settings

Without transcription enabled, the bot won't receive transcript events.

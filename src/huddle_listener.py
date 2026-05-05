import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from .transcript_processor import process_huddle_transcript
from .note_generator import generate_notes_and_todos

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


@app.event("huddle_transcript_ready")
def handle_huddle_transcript(event, client, say):
    """Triggered when a huddle transcript becomes available."""
    channel_id = event.get("channel_id")
    huddle_id = event.get("huddle_id")
    transcript_file_id = event.get("file_id")

    logger.info(f"Huddle transcript ready: {huddle_id} in channel {channel_id}")

    try:
        transcript_content = fetch_transcript(client, transcript_file_id)
        participants = event.get("participants", [])

        processed = process_huddle_transcript(
            transcript=transcript_content,
            participants=participants,
            huddle_id=huddle_id
        )

        notes = generate_notes_and_todos(processed)

        post_notes_to_channel(client, channel_id, notes, huddle_id)

    except Exception as e:
        logger.error(f"Failed to process huddle transcript: {e}")


@app.event("huddle_ended")
def handle_huddle_ended(event, client):
    """Triggered when a huddle ends - transcript may not be ready yet."""
    huddle_id = event.get("huddle_id")
    channel_id = event.get("channel_id")
    logger.info(f"Huddle ended: {huddle_id} in {channel_id}, waiting for transcript...")


def fetch_transcript(client, file_id: str) -> str:
    """Fetch the transcript content from Slack."""
    file_info = client.files_info(file=file_id)
    file_data = file_info.get("file", {})

    if "url_private_download" in file_data:
        import requests
        headers = {"Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"}
        response = requests.get(file_data["url_private_download"], headers=headers)
        return response.text

    return file_data.get("plain_text", "")


def post_notes_to_channel(client, channel_id: str, notes: dict, huddle_id: str):
    """Post the generated notes back to the channel."""
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Huddle Notes", "emoji": True}
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Summary:*\n{notes['summary']}"}
        }
    ]

    if notes.get("key_points"):
        points_text = "\n".join(f"• {point}" for point in notes["key_points"])
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Key Points:*\n{points_text}"}
        })

    if notes.get("action_items"):
        todos_text = "\n".join(
            f"• {item['task']}" + (f" (@{item['assignee']})" if item.get("assignee") else "")
            for item in notes["action_items"]
        )
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Action Items:*\n{todos_text}"}
        })

    if notes.get("decisions"):
        decisions_text = "\n".join(f"• {d}" for d in notes["decisions"])
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Decisions Made:*\n{decisions_text}"}
        })

    client.chat_postMessage(
        channel=channel_id,
        text=f"Huddle notes for {huddle_id}",
        blocks=blocks
    )


def start():
    """Start the Slack app in Socket Mode."""
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    logger.info("Starting Huddle Notes Bot...")
    handler.start()


if __name__ == "__main__":
    start()

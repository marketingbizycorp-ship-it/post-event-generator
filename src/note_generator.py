import os
import json
from typing import Optional
from .transcript_processor import ProcessedTranscript

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


def generate_notes_and_todos(transcript: ProcessedTranscript) -> dict:
    """Generate structured notes and action items from a processed transcript."""

    if HAS_ANTHROPIC and os.environ.get("ANTHROPIC_API_KEY"):
        return generate_with_claude(transcript)
    elif HAS_OPENAI and os.environ.get("OPENAI_API_KEY"):
        return generate_with_openai(transcript)
    else:
        return generate_basic_notes(transcript)


def generate_with_claude(transcript: ProcessedTranscript) -> dict:
    """Use Claude to generate intelligent notes."""
    client = anthropic.Anthropic()

    prompt = build_prompt(transcript)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    return parse_llm_response(response.content[0].text)


def generate_with_openai(transcript: ProcessedTranscript) -> dict:
    """Use OpenAI to generate notes."""
    client = openai.OpenAI()

    prompt = build_prompt(transcript)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )

    return parse_llm_response(response.choices[0].message.content)


def generate_basic_notes(transcript: ProcessedTranscript) -> dict:
    """Fallback: generate basic notes without AI."""
    speakers = list(set(s.speaker for s in transcript.segments if s.speaker != "Unknown"))

    return {
        "summary": f"Huddle with {len(speakers)} participants lasting ~{transcript.duration_minutes or 'unknown'} minutes.",
        "key_points": [s.text[:100] + "..." if len(s.text) > 100 else s.text
                       for s in transcript.segments[:5]],
        "action_items": [],
        "decisions": [],
        "participants": speakers
    }


def build_prompt(transcript: ProcessedTranscript) -> str:
    """Build the prompt for LLM note generation."""
    conversation = "\n".join(
        f"{s.speaker}: {s.text}" for s in transcript.segments
    )

    return f"""Analyze this huddle transcript and create structured notes.

TRANSCRIPT:
{conversation}

PARTICIPANTS: {', '.join(transcript.participants) if transcript.participants else 'Unknown'}
DURATION: {transcript.duration_minutes or 'Unknown'} minutes

Generate a JSON response with this structure:
{{
    "summary": "2-3 sentence summary of what was discussed",
    "key_points": ["point 1", "point 2", ...],
    "action_items": [
        {{"task": "description", "assignee": "person or null", "deadline": "date or null"}}
    ],
    "decisions": ["decision 1", "decision 2", ...],
    "participants": ["name1", "name2", ...]
}}

Focus on:
- Clear, concise summary
- Extracting specific action items with owners when mentioned
- Capturing any decisions or agreements made
- Key discussion points

Respond with only valid JSON."""


def parse_llm_response(response: str) -> dict:
    """Parse LLM response to extract structured notes."""
    try:
        json_match = response.strip()
        if json_match.startswith("```"):
            json_match = json_match.split("```")[1]
            if json_match.startswith("json"):
                json_match = json_match[4:]

        return json.loads(json_match)
    except json.JSONDecodeError:
        return {
            "summary": response[:500],
            "key_points": [],
            "action_items": [],
            "decisions": [],
            "participants": []
        }

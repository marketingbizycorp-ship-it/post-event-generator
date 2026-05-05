import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class TranscriptSegment:
    speaker: str
    text: str
    timestamp: Optional[str] = None


@dataclass
class ProcessedTranscript:
    segments: list[TranscriptSegment]
    participants: list[str]
    duration_minutes: Optional[int]
    raw_text: str
    huddle_id: str


def process_huddle_transcript(
    transcript: str,
    participants: list[str],
    huddle_id: str
) -> ProcessedTranscript:
    """Parse and structure a huddle transcript."""
    segments = parse_transcript_segments(transcript)
    duration = estimate_duration(segments)

    return ProcessedTranscript(
        segments=segments,
        participants=participants,
        duration_minutes=duration,
        raw_text=transcript,
        huddle_id=huddle_id
    )


def parse_transcript_segments(transcript: str) -> list[TranscriptSegment]:
    """Parse transcript into speaker segments."""
    segments = []

    pattern = r'\[?(\d{1,2}:\d{2}(?::\d{2})?)\]?\s*([^:]+):\s*(.+?)(?=\[?\d{1,2}:\d{2}|$)'
    matches = re.findall(pattern, transcript, re.DOTALL)

    if matches:
        for timestamp, speaker, text in matches:
            segments.append(TranscriptSegment(
                speaker=speaker.strip(),
                text=text.strip(),
                timestamp=timestamp
            ))
    else:
        lines = transcript.strip().split('\n')
        for line in lines:
            speaker_match = re.match(r'^([^:]+):\s*(.+)$', line)
            if speaker_match:
                segments.append(TranscriptSegment(
                    speaker=speaker_match.group(1).strip(),
                    text=speaker_match.group(2).strip()
                ))
            elif line.strip():
                segments.append(TranscriptSegment(
                    speaker="Unknown",
                    text=line.strip()
                ))

    return segments


def estimate_duration(segments: list[TranscriptSegment]) -> Optional[int]:
    """Estimate huddle duration from timestamps."""
    timestamps = [s.timestamp for s in segments if s.timestamp]
    if len(timestamps) < 2:
        return None

    try:
        first = parse_timestamp(timestamps[0])
        last = parse_timestamp(timestamps[-1])
        return (last - first) // 60
    except (ValueError, TypeError):
        return None


def parse_timestamp(ts: str) -> int:
    """Parse timestamp string to seconds."""
    parts = ts.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0

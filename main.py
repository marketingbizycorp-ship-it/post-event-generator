#!/usr/bin/env python3
"""
Slack Huddle Notes Bot

Automatically generates notes and action items when a Slack huddle ends.
"""
from src.huddle_listener import start

if __name__ == "__main__":
    start()

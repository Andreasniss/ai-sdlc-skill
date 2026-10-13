#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andreas Nissen
# SPDX-License-Identifier: Apache-2.0
"""Synthetic SessionStart probe: no files, network, tool decisions, or context."""
import json
import sys


def main():
    try:
        event = json.load(sys.stdin)
    except (ValueError, UnicodeError):
        return 1
    if not isinstance(event, dict) or event.get("hook_event_name") != "SessionStart":
        return 1
    if event.get("source") != "startup":
        return 1
    # Never echo payload data (which could contain private paths or identifiers).
    print("ai-sdlc synthetic SessionStart probe received", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

# utils/helpers.py
# Shared helper functions used by all agent nodes

import json
import re


def parse_json_response(text):
    text = text.replace("```json", "").replace("```", "").strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except Exception:
        pass

    # If that didn't work, try to find a JSON object somewhere inside the text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    # Nothing worked
    return {}


def parse_json_list(text):
    """
    Tries to parse a JSON array from the LLM's response text.
    Returns an empty list if parsing fails.
    """
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
    except Exception:
        pass

    # Try to find a JSON array somewhere inside the text
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, list):
                return result
        except Exception:
            pass

    return []

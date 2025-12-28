"""
Helper utilities for XStore Customer Support Agent.
"""

from typing import Dict, Any


def format_response_json(result: Dict[str, Any]) -> Dict[str, Any]:
    """Format response for API/JSON output."""
    return {
        "success": True,
        "data": {
            "query": result.get("query", ""),
            "language": result.get("language_code", "tr"),
            "category": result.get("category_code", "general"),
            "sentiment": result.get("sentiment_code", "neutral"),
            "response": result.get("response", "")
        }
    }


def format_error_json(error: str) -> Dict[str, Any]:
    """Format error for API/JSON output."""
    return {
        "success": False,
        "error": str(error)
    }


def validate_language(language: str) -> str:
    """Validate and normalize language code."""
    if language and language.lower() in ["tr", "en", "turkish", "english"]:
        return "tr" if language.lower() in ["tr", "turkish"] else "en"
    return None


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

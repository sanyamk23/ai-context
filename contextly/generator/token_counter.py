"""Token counting utilities."""

from __future__ import annotations

import re


def count_tokens_approx(text: str) -> int:
    """Approximate token count using word-based heuristic.

    This is a fast, dependency-free estimate. For precise counts,
    use tiktoken (optional dependency).
    """
    words = len(text.split())
    return int(words * 1.3)


def count_tokens_tiktoken(text: str, model: str = "cl100k_base") -> int:
    """Count tokens precisely using tiktoken (if available)."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding(model)
        return len(enc.encode(text))
    except ImportError:
        return count_tokens_approx(text)


def format_tokens(count: int) -> str:
    """Format token count for display."""
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    if count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)

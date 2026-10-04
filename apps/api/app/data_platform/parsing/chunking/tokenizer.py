"""
Token estimation utilities for WaterDIP chunking.

Exact model-specific tokenization belongs to the embedding layer.
The chunking layer uses a deterministic approximation.
"""

from __future__ import annotations

import re


_TOKEN_RE = re.compile(
    r"\w+|[^\w\s]",
    flags=re.UNICODE,
)


def tokenize(
    text: str,
) -> list[str]:
    """Return deterministic approximate lexical tokens."""

    return _TOKEN_RE.findall(text)


def count_tokens(
    text: str,
) -> int:
    """Estimate token count without depending on an LLM provider."""

    if not text:
        return 0

    return len(tokenize(text))


def join_tokens(
    tokens: list[str],
) -> str:
    """
    Join approximate tokens into readable text.

    This is only used for fallback splitting. Structural chunkers preserve
    source text whenever possible.
    """

    if not tokens:
        return ""

    output = tokens[0]

    punctuation = {
        ".",
        ",",
        ":",
        ";",
        "!",
        "?",
        ")",
        "]",
        "}",
        "%",
    }

    opening = {
        "(",
        "[",
        "{",
    }

    for index, token in enumerate(
        tokens[1:],
        start=1,
    ):
        previous = tokens[index - 1]

        if token in punctuation:
            output += token
        elif previous in opening:
            output += token
        else:
            output += f" {token}"

    return output.strip()
"""Thin wrappers around the Anthropic SDK for text + multimodal (image) calls."""

from __future__ import annotations

import base64
from typing import Any, Iterable, Optional

import config.config as config


def _to_text(response: Any) -> str:
    """Extract concatenated text from an Anthropic Messages API response."""
    if response is None:
        return ""
    content = getattr(response, "content", None)
    if not content:
        return ""
    parts = []
    for block in content:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    return "".join(parts).strip()


def call_text(
    anthropic_client,
    system: str,
    user: str,
    *,
    max_tokens: int = 8192,
    model: str = config.DEFAULT_DOCS_MODEL,
) -> str:
    """Single-shot text completion via Claude. Returns the assistant text."""
    response = anthropic_client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return _to_text(response)


def encode_image_b64(image_path: str) -> str:
    """Read an image file and return its base64 representation."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def _guess_media_type(image_path: str) -> str:
    lower = image_path.lower()
    if lower.endswith(".jpg") or lower.endswith(".jpeg"):
        return "image/jpeg"
    if lower.endswith(".webp"):
        return "image/webp"
    if lower.endswith(".gif"):
        return "image/gif"
    return "image/png"


def call_with_image(
    anthropic_client,
    system: str,
    user_text: str,
    image_path: str,
    *,
    max_tokens: int = 8192,
    model: str = config.DEFAULT_DOCS_MODEL,
) -> str:
    """Single-shot completion with one image + one user text block."""
    encoded = encode_image_b64(image_path)
    media_type = _guess_media_type(image_path)
    response = anthropic_client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": encoded,
                        },
                    },
                    {"type": "text", "text": user_text},
                ],
            }
        ],
    )
    return _to_text(response)

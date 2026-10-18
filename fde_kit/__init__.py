"""Shared helpers for the Forward Deployed Engineer exercises.

Everything here runs offline. `FakeLLM` lets tests script model behaviour
deterministically; `AnthropicLLM` is an optional adapter for real calls.
"""
from .llm import AnthropicLLM, FakeLLM, LLMResponse, ToolCall, get_llm
from .text import cosine, hash_embed, tokenize

__all__ = [
    "AnthropicLLM", "FakeLLM", "LLMResponse", "ToolCall", "get_llm",
    "cosine", "hash_embed", "tokenize",
]

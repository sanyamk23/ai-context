"""Token cost estimation for major AI providers."""

from __future__ import annotations

from dataclasses import dataclass


# Approximate tokens per word (English average)
TOKENS_PER_WORD = 1.3

# Provider pricing (USD per 1M tokens, as of early 2026)
PROVIDERS = {
    "Claude Sonnet 4": {"input": 3.00, "output": 15.00},
    "Claude Opus 4": {"input": 15.00, "output": 75.00},
    "Claude Haiku 3.5": {"input": 0.80, "output": 4.00},
    "GPT-4o": {"input": 2.50, "output": 10.00},
    "GPT-4.1": {"input": 2.00, "output": 8.00},
    "Gemini 2.5 Pro": {"input": 1.25, "output": 10.00},
    "Gemini 2.5 Flash": {"input": 0.15, "output": 0.60},
}


@dataclass
class CostEstimate:
    provider: str
    tokens_without_context: int
    tokens_with_context: int
    tokens_saved: int
    cost_without_context: float
    cost_with_context: float
    cost_saved: float
    savings_percent: float
    monthly_savings_10_sessions: float
    monthly_savings_50_sessions: float


def estimate_tokens(text: str) -> int:
    """Estimate token count from text (word-based approximation)."""
    words = len(text.split())
    return int(words * TOKENS_PER_WORD)


def estimate_cost_per_session(
    without_context_tokens: int,
    with_context_tokens: int,
) -> list[CostEstimate]:
    """Estimate cost savings across all providers."""
    results = []

    for provider, prices in PROVIDERS.items():
        cost_without = (without_context_tokens / 1_000_000) * prices["input"]
        cost_with = (with_context_tokens / 1_000_000) * prices["input"]
        saved = cost_without - cost_with
        pct = (saved / cost_without * 100) if cost_without > 0 else 0

        results.append(CostEstimate(
            provider=provider,
            tokens_without_context=without_context_tokens,
            tokens_with_context=with_context_tokens,
            tokens_saved=without_context_tokens - with_context_tokens,
            cost_without_context=cost_without,
            cost_with_context=cost_with,
            cost_saved=saved,
            savings_percent=pct,
            monthly_savings_10_sessions=saved * 10,
            monthly_savings_50_sessions=saved * 50,
        ))

    return sorted(results, key=lambda x: x.monthly_savings_50_sessions, reverse=True)


def estimate_context_overhead(context_tokens: int, base_tokens_per_session: int = 8000) -> dict:
    """Estimate what percentage of a session is wasted on context vs. actual work."""
    total = base_tokens_per_session + context_tokens
    overhead_pct = (context_tokens / total * 100) if total > 0 else 0
    return {
        "context_tokens": context_tokens,
        "base_session_tokens": base_tokens_per_session,
        "total_tokens": total,
        "overhead_percent": round(overhead_pct, 1),
        "effective_work_tokens": base_tokens_per_session,
    }

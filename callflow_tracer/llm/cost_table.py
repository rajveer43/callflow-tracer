"""LLM token pricing table (input $/M tokens, output $/M tokens)."""

from __future__ import annotations

# (input_cost_per_million, output_cost_per_million) in USD
PRICING: dict[str, tuple[float, float]] = {
    # Anthropic
    "claude-opus-4-7":                  (15.00, 75.00),
    "claude-opus-4-5":                  (15.00, 75.00),
    "claude-sonnet-4-6":                (3.00,  15.00),
    "claude-sonnet-4-5":                (3.00,  15.00),
    "claude-haiku-4-5":                 (0.25,   1.25),
    "claude-3-5-sonnet-20241022":       (3.00,  15.00),
    "claude-3-5-haiku-20241022":        (0.80,   4.00),
    "claude-3-opus-20240229":           (15.00, 75.00),
    "claude-3-sonnet-20240229":         (3.00,  15.00),
    "claude-3-haiku-20240307":          (0.25,   1.25),
    # OpenAI
    "gpt-4o":                           (2.50,  10.00),
    "gpt-4o-mini":                      (0.15,   0.60),
    "gpt-4-turbo":                      (10.00, 30.00),
    "gpt-4":                            (30.00, 60.00),
    "gpt-3.5-turbo":                    (0.50,   1.50),
    "o1":                               (15.00, 60.00),
    "o1-mini":                          (3.00,  12.00),
    "o3-mini":                          (1.10,   4.40),
}

_FALLBACK_COST = (1.00, 3.00)  # conservative fallback for unknown models


def _normalize_model(model: str) -> str:
    """Strip date suffixes and lowercase for fuzzy matching."""
    return model.lower().split(":")[0]


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Return total USD cost for a single LLM call."""
    key = _normalize_model(model)
    # Exact match first, then prefix match
    prices = PRICING.get(key)
    if prices is None:
        for table_key, table_prices in PRICING.items():
            if key.startswith(table_key) or table_key.startswith(key):
                prices = table_prices
                break
    if prices is None:
        prices = _FALLBACK_COST

    input_cost_per_m, output_cost_per_m = prices
    return (input_tokens * input_cost_per_m + output_tokens * output_cost_per_m) / 1_000_000

from __future__ import annotations

from typing import Final

from prometheus_client import Counter, Histogram


REQUESTS_TOTAL: Final = Counter(
    "requests_total",
    "Total HTTP requests",
    ["path", "method", "code"],
)

REQUEST_LATENCY_MS: Final = Histogram(
    "request_latency_ms",
    "Request latency in milliseconds",
    ["path", "method"],
    buckets=(5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000),
)

PROVIDER_LATENCY_MS: Final = Histogram(
    "provider_latency_ms",
    "LLM or embedding provider latency in milliseconds",
    ["provider", "operation"],
    buckets=(10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000),
)

TOKENS_TOTAL: Final = Counter(
    "tokens_total",
    "Estimated token usage",
    ["direction", "provider", "model"],
)

WATERDIP_DIAGNOSES_TOTAL: Final = Counter(
    "waterdip_diagnoses_total",
    "Total WaterDIP diagnostic requests",
    ["severity"],
)
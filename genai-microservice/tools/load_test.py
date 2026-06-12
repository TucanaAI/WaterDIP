import asyncio
import argparse
import time
import json
import httpx
from typing import Any

async def worker(client: httpx.AsyncClient, url: str, payload: dict[str, Any], results: list[float | None], timeout: float) -> None:
    try:
        t0 = time.perf_counter()
        r = await client.post(url, json=payload, timeout=timeout)
        dt = (time.perf_counter() - t0) * 1000.0
        results.append(dt)
        r.raise_for_status()
    except Exception:
        results.append(None)

async def main(url: str, concurrency: int, requests: int, timeout: float, out_path: str | None) -> None:
    payload = {"prompt": "ping", "max_tokens": 32}
    results: list[float | None] = []

    async with httpx.AsyncClient() as client:
        sem = asyncio.Semaphore(concurrency)

        async def run_one() -> None:
            async with sem:
                await worker(client, url, payload, results, timeout)

        await asyncio.gather(*[asyncio.create_task(run_one()) for _ in range(requests)])

    ok = [x for x in results if x is not None]
    ok.sort()
    fail = len(results) - len(ok)

    def pct(p: int) -> float | None:
        return ok[int(len(ok) * p / 100)] if ok else None

    summary = {
        "requests": len(results),
        "ok": len(ok),
        "fail": fail,
        "latency_ms": {
            "p50": pct(50),
            "p90": pct(90),
            "p95": pct(95),
            "max": ok[-1] if ok else None,
        },
    }

    print(json.dumps(summary, indent=2))

    # Optionally save raw data for plotting
    if out_path:
        out_data = {"summary": summary, "latencies_ms": ok}
        with open(out_path, "w") as f:
            json.dump(out_data, f, indent=2)
        print(f"✅ Saved raw latency data to {out_path}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Async load tester for GenAI microservice")
    ap.add_argument("--url", required=True, help="Target URL (e.g., https://api.example.com/chat)")
    ap.add_argument("--concurrency", type=int, default=50)
    ap.add_argument("--requests", type=int, default=1000)
    ap.add_argument("--timeout", type=float, default=10.0, help="Per-request timeout in seconds")
    ap.add_argument("--out", type=str, help="Optional path to write detailed JSON results")
    args = ap.parse_args()

    asyncio.run(main(args.url, args.concurrency, args.requests, args.timeout, args.out))


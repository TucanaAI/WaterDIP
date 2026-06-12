import json
import matplotlib.pyplot as plt
import sys

if len(sys.argv) < 2:
    print("Usage: python tools/plot_loadtest.py reports/loadtest_raw_*.json")
    sys.exit(1)

file = sys.argv[1]

with open(file, "r") as f:
    data = json.load(f)

summary = data.get("summary", {})
latencies = data.get("latencies_ms", [])

if not latencies:
    print("No raw latencies found. Run load_test.py with --out <file>.")
    sys.exit(1)

plt.figure(figsize=(10, 4))

# Histogram
plt.hist(latencies, bins=40, color="#2563eb", alpha=0.8, edgecolor="white")
plt.title("Latency Distribution (ms)")
plt.xlabel("Latency (ms)")
plt.ylabel("Request Count")
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("reports/latency_histogram.png", dpi=150)
print("✅ Saved histogram to reports/latency_histogram.png")

# Optional summary bar chart
percentiles = summary.get("latency_ms", {})
if percentiles:
    plt.figure(figsize=(6, 4))
    plt.bar(percentiles.keys(), percentiles.values(), color="#059669")
    plt.title("Latency Summary (ms)")
    plt.xlabel("Percentile")
    plt.ylabel("Latency (ms)")
    plt.tight_layout()
    plt.savefig("reports/latency_summary.png", dpi=150)
    print("✅ Saved summary to reports/latency_summary.png")


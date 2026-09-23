"""Replay a captured tool-payload session through each output encoding and compare token counts.

Usage:
    OSASCRIPT_MCP_CAPTURE=/tmp/sog-payloads.jsonl <run whatever exercises the server>
    uv run python bench/replay.py /tmp/sog-payloads.jsonl

Each line of the capture file is one `{"tool": ..., "payload": ...}` record, written by
`osascript_mcp.server.encode_payload` when OSASCRIPT_MCP_CAPTURE is set (see TASK-001.13).
This script re-encodes every captured payload as pretty JSON (today's baseline), minified
JSON, and TOON, then reports token counts per tool and in total — the actual measurement
behind the TASK-001.13 decision, as opposed to the synthetic estimates in the task notes.
"""

import json
import os
import sys
import tiktoken
import toon_format
from collections import defaultdict

_ENC = tiktoken.get_encoding("o200k_base")


def _tiktoken_len(s: str) -> int:
    return len(_ENC.encode(s))


def _anthropic_len(client, model: str, s: str) -> int:
    return client.messages.count_tokens(model=model, messages=[{"role": "user", "content": s}]).input_tokens


def load_capture(path: str) -> list[dict]:
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def encodings_for(payload) -> dict[str, str]:
    return {
        "json-i2": json.dumps(payload, indent=2),
        "json-min": json.dumps(payload, separators=(",", ":")),
        "toon": toon_format.encode(payload),
    }


def main() -> None:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <capture.jsonl>", file=sys.stderr)
        sys.exit(1)

    records = load_capture(sys.argv[1])
    if not records:
        print("No captured records found — nothing to replay.", file=sys.stderr)
        sys.exit(1)

    anthropic_client = None
    anthropic_model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
    if os.environ.get("ANTHROPIC_API_KEY"):
        import anthropic

        anthropic_client = anthropic.Anthropic()

    per_tool = defaultdict(lambda: {"calls": 0, "json-i2": 0, "json-min": 0, "toon": 0})
    per_tool_anthropic = defaultdict(lambda: {"json-i2": 0, "json-min": 0, "toon": 0})

    for rec in records:
        tool = rec.get("tool") or "(unknown)"
        encs = encodings_for(rec["payload"])
        row = per_tool[tool]
        row["calls"] += 1
        for name, text in encs.items():
            row[name] += _tiktoken_len(text)
            if anthropic_client:
                per_tool_anthropic[tool][name] += _anthropic_len(anthropic_client, anthropic_model, text)

    header = f"{'tool':<28} {'calls':>5} {'json-i2':>8} {'json-min':>9} {'toon':>7} {'vs i2':>7} {'vs min':>7}"
    print(f"tiktoken (o200k_base) — {len(records)} captured calls across {len(per_tool)} tools\n")
    print(header)
    totals = {"calls": 0, "json-i2": 0, "json-min": 0, "toon": 0}
    for tool in sorted(per_tool):
        row = per_tool[tool]
        vs_i2 = 100 * (row["json-i2"] - row["toon"]) / row["json-i2"] if row["json-i2"] else 0
        vs_min = 100 * (row["json-min"] - row["toon"]) / row["json-min"] if row["json-min"] else 0
        print(
            f"{tool:<28} {row['calls']:>5} {row['json-i2']:>8} {row['json-min']:>9} "
            f"{row['toon']:>7} {vs_i2:>6.1f}% {vs_min:>6.1f}%"
        )
        for k in totals:
            totals[k] += row[k]
    vs_i2 = 100 * (totals["json-i2"] - totals["toon"]) / totals["json-i2"] if totals["json-i2"] else 0
    vs_min = 100 * (totals["json-min"] - totals["toon"]) / totals["json-min"] if totals["json-min"] else 0
    print("-" * len(header))
    print(
        f"{'TOTAL':<28} {totals['calls']:>5} {totals['json-i2']:>8} {totals['json-min']:>9} "
        f"{totals['toon']:>7} {vs_i2:>6.1f}% {vs_min:>6.1f}%"
    )

    if anthropic_client:
        print(f"\nAnthropic count_tokens ({anthropic_model}):\n")
        print(header)
        a_totals = {"json-i2": 0, "json-min": 0, "toon": 0}
        for tool in sorted(per_tool_anthropic):
            row = per_tool_anthropic[tool]
            calls = per_tool[tool]["calls"]
            vs_i2 = 100 * (row["json-i2"] - row["toon"]) / row["json-i2"] if row["json-i2"] else 0
            vs_min = 100 * (row["json-min"] - row["toon"]) / row["json-min"] if row["json-min"] else 0
            print(
                f"{tool:<28} {calls:>5} {row['json-i2']:>8} {row['json-min']:>9} {row['toon']:>7} {vs_i2:>6.1f}% {vs_min:>6.1f}%"
            )
            for k in a_totals:
                a_totals[k] += row[k]
        vs_i2 = 100 * (a_totals["json-i2"] - a_totals["toon"]) / a_totals["json-i2"] if a_totals["json-i2"] else 0
        vs_min = 100 * (a_totals["json-min"] - a_totals["toon"]) / a_totals["json-min"] if a_totals["json-min"] else 0
        print("-" * len(header))
        print(
            f"{'TOTAL':<28} {totals['calls']:>5} {a_totals['json-i2']:>8} {a_totals['json-min']:>9} "
            f"{a_totals['toon']:>7} {vs_i2:>6.1f}% {vs_min:>6.1f}%"
        )
    else:
        print(
            "\n(Set ANTHROPIC_API_KEY to also report exact Claude token counts via "
            "/v1/messages/count_tokens — the tiktoken numbers above are a fast local proxy, "
            "not Claude's actual tokenizer.)"
        )


if __name__ == "__main__":
    main()

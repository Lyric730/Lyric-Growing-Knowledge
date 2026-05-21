"""
Step 1: 从 aihot.virxact.com 抓取昨日 AI 圈热点 → raw.json

API:  https://aihot.virxact.com/api/public/items?mode=all&since=<ISO>&take=<N>

Output schema (per item):
  - id, title, title_en, url, source, publishedAt, summary, category

Usage:
    python pipeline/fetch_aihot.py <YYYY-MM-DD> [--take 50]

Example:
    python pipeline/fetch_aihot.py 2026-05-15 --take 50
    → daily/2026-05-15/work/raw.json
"""
import argparse
import json
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

import requests

API_BASE = "https://aihot.virxact.com/api/public/items"


def fetch_for_date(target_date: date, take: int = 100) -> dict:
    """
    API 经实测忽略 since/until — 总是返回最新 take 条 desc by publishedAt。
    所以策略：take 取大（默认 100，够覆盖 1-2 天），client-side 过滤到 target_date。
    """
    params = {"mode": "all", "take": take}
    resp = requests.get(
        API_BASE,
        params=params,
        headers={"User-Agent": "self-media-daily/1.0"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("date", help="目标日期 YYYY-MM-DD（抓这一天的全天热点）")
    parser.add_argument("--take", type=int, default=100, help="API 抓取候选数（client filter 前）")
    parser.add_argument("--root", default=".", help="项目根目录")
    args = parser.parse_args()

    target = date.fromisoformat(args.date)
    out_dir = Path(args.root) / "daily" / args.date / "work"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "raw.json"

    print(f"→ fetch_aihot {target.isoformat()} (take={args.take})")
    data = fetch_for_date(target, take=args.take)
    raw_items = data.get("items", [])

    # Client-side strict filter: only items whose publishedAt date matches target.
    # API since/until is best-effort; some items leak across UTC boundaries.
    target_prefix = target.isoformat()
    items = [i for i in raw_items if i.get("publishedAt", "").startswith(target_prefix)]
    dropped = len(raw_items) - len(items)
    data["items"] = items
    data["count"] = len(items)

    out_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"✓ {len(items)} items → {out_path}" + (f" ({dropped} cross-day dropped)" if dropped else ""))
    if items:
        print(f"  first: {items[0].get('title', '')[:60]}")
        print(f"  last:  {items[-1].get('title', '')[:60]}")


if __name__ == "__main__":
    main()

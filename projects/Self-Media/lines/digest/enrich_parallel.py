"""
Step 3: 对 raw.json 里每条候选做精读 → enriched_raw.json

策略：
- X (x.com / twitter.com) 链接 → OpenCLI `twitter thread <id> --format json`
                                  抓原推 text + likes + retweets + replies
- 非 X 链接                       → requests + extract og:title / og:image /
                                  og:description + first <p> 正文片段

输出 schema (per item):
  原 raw item 字段（id, title, url, source, publishedAt, summary, category）
  + enrichment 字段：
      - platform: "x" | "ithome" | "the-decoder" | ...
      - og_title / og_description / og_image
      - tweet_text / tweet_likes / tweet_retweets / tweet_replies (X only)
      - body_excerpt (非 X 文章首段)

Usage:
    python lines/digest/enrich_parallel.py <YYYY-MM-DD> [--limit 30]
"""
import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import requests


X_TWEET_RE = re.compile(r"(?:twitter\.com|x\.com)/[^/]+/status/(\d+)")
NVM_INIT = "source ~/.nvm/nvm.sh && nvm use 22 > /dev/null && "


def host_of(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def is_x_link(url: str) -> bool:
    return host_of(url) in ("x.com", "twitter.com")


def enrich_x(url: str) -> dict:
    """Use opencli twitter thread to fetch tweet text + interactions + replies."""
    m = X_TWEET_RE.search(url)
    if not m:
        return {"error": "no tweet id", "url": url}
    tweet_id = m.group(1)
    cmd = f"{NVM_INIT}opencli twitter thread {tweet_id} --format json 2>/dev/null"
    try:
        result = subprocess.run(
            ["bash", "-lc", cmd],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            return {"error": f"opencli failed: rc={result.returncode}", "url": url}
        data = json.loads(result.stdout)
        if not data:
            return {"error": "empty", "url": url}
        # data is a list — index 0 is original tweet, rest are replies
        original = data[0]
        replies = data[1:]
        return {
            "tweet_text": original.get("text", ""),
            "tweet_author": original.get("author", ""),
            "tweet_likes": original.get("likes", 0),
            "tweet_retweets": original.get("retweets", 0),
            "tweet_created_at": original.get("created_at", ""),
            "replies_count": len(replies),
            "top_replies": [
                {
                    "author": r.get("author"),
                    "text": (r.get("text") or "")[:280],
                    "likes": r.get("likes", 0),
                }
                for r in sorted(replies, key=lambda r: r.get("likes", 0), reverse=True)[:5]
            ],
        }
    except subprocess.TimeoutExpired:
        return {"error": "timeout", "url": url}
    except Exception as e:
        return {"error": str(e), "url": url}


def enrich_article(url: str) -> dict:
    """Extract og:title / og:image / og:description + first <p> from article URL."""
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; self-media-daily/1.0)"},
            timeout=20,
            allow_redirects=True,
        )
        if resp.status_code != 200:
            return {"error": f"http {resp.status_code}", "url": url}
        html = resp.text
        out: dict = {"final_url": resp.url}
        for prop, key in [
            ("og:title", "og_title"),
            ("og:image", "og_image"),
            ("og:description", "og_description"),
        ]:
            m = re.search(
                rf'<meta\s+(?:[^>]*\s)?property=["\']?{prop}["\']?[^>]*content=["\']([^"\']+)["\']',
                html, re.I,
            )
            if not m:
                m = re.search(
                    rf'<meta\s+(?:[^>]*\s)?content=["\']([^"\']+)["\'][^>]*property=["\']?{prop}["\']?',
                    html, re.I,
                )
            if m:
                out[key] = m.group(1)
        # crude first paragraph for body_excerpt
        m = re.search(r"<p[^>]*>([^<]{50,400})</p>", html, re.S)
        if m:
            out["body_excerpt"] = re.sub(r"\s+", " ", m.group(1)).strip()
        return out
    except requests.RequestException as e:
        return {"error": str(e), "url": url}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("date", help="目标日期 YYYY-MM-DD")
    parser.add_argument("--limit", type=int, default=30, help="精读前 N 条（默认 30）")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = Path(args.root)
    raw_path = root / "daily" / args.date / "digest" / "work" / "raw.json"
    out_path = root / "daily" / args.date / "digest" / "work" / "enriched_raw.json"
    if not raw_path.exists():
        raise SystemExit(f"missing: {raw_path}  (run fetch_aihot.py first)")

    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    items = raw.get("items", [])[: args.limit]
    print(f"→ enrich {len(items)} items from {raw_path}")

    enriched: list[dict] = []
    x_count = a_count = err = 0
    for idx, item in enumerate(items, 1):
        url = item.get("url", "")
        platform = host_of(url) or "unknown"
        out = dict(item)
        out["platform"] = platform
        if is_x_link(url):
            extra = enrich_x(url)
            x_count += 1
            kind = "x"
        else:
            extra = enrich_article(url)
            a_count += 1
            kind = "article"
        out.update(extra)
        if "error" in extra:
            err += 1
        enriched.append(out)
        title_short = item.get("title", "")[:40]
        status = "✗" if "error" in extra else "✓"
        print(f"  {status} [{idx:>2}/{len(items)}] {kind:7s}  {title_short}")

    out_path.write_text(
        json.dumps({"items": enriched, "count": len(enriched)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"✓ {len(enriched)} enriched ({x_count} X / {a_count} articles, {err} errors) → {out_path}")


if __name__ == "__main__":
    main()

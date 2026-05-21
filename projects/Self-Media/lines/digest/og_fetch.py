"""
Step 3 附加：抓 hero 素材（og:image / 推文 media）→ daily/<date>/digest/work/assets/

读 enriched_raw.json，对每条尽量抓一张 hero 候选图：
- 文章链接：curl 下载 og_image (enriched_raw 里已有 URL)
- X 链接：用 OpenCLI `twitter download --tweet-url <url>` （progressive；
                没 media 返回 "No media found" 不报错）

输出：work/assets/<item-id>.<ext>（jpg/png/webp）

非 fatal — 抓不到的项目跳过，pipeline 后续 fallback 到 SVG/CSS hero。

Usage:
    python lines/digest/og_fetch.py <YYYY-MM-DD>
"""
import argparse
import json
import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import requests

NVM_INIT = "source ~/.nvm/nvm.sh && nvm use 22 > /dev/null && "


def ext_of(url: str) -> str:
    path = urlparse(url).path.lower()
    for e in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
        if path.endswith(e):
            return e
    return ".jpg"


def fetch_og_image(url: str, dest: Path) -> bool:
    try:
        r = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; self-media-daily/1.0)"},
            timeout=20,
            stream=True,
        )
        if r.status_code != 200:
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return dest.stat().st_size > 1000  # > 1KB sanity
    except requests.RequestException:
        return False


def fetch_x_media(tweet_url: str, dest_dir: Path) -> bool:
    """opencli twitter download --tweet-url <url> --output <dir>"""
    dest_dir.mkdir(parents=True, exist_ok=True)
    cmd = (
        f"{NVM_INIT}opencli twitter download "
        f"--tweet-url '{tweet_url}' --output '{dest_dir}' --format json 2>/dev/null"
    )
    try:
        result = subprocess.run(
            ["bash", "-lc", cmd], capture_output=True, text=True, timeout=45,
        )
        if result.returncode != 0:
            return False
        # opencli writes nested: <dest_dir>/tweets/tweet_N.{jpg,mp4} — use rglob
        return any(
            p.is_file() and p.stat().st_size > 1000
            for p in dest_dir.rglob("*")
            if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4")
        )
    except (subprocess.TimeoutExpired, OSError):
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("date")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = Path(args.root)
    enriched_path = root / "daily" / args.date / "digest" / "work" / "enriched_raw.json"
    assets_dir = root / "daily" / args.date / "digest" / "work" / "assets"
    if not enriched_path.exists():
        raise SystemExit(f"missing: {enriched_path}  (run enrich_parallel.py first)")

    data = json.loads(enriched_path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    print(f"→ og_fetch {len(items)} items → {assets_dir}")

    ok_og = ok_x = miss = 0
    for idx, item in enumerate(items, 1):
        item_id = item.get("id", f"item-{idx}")
        platform = item.get("platform", "")
        url = item.get("url", "")
        og_url = item.get("og_image")

        # Article: try og:image
        if og_url:
            dest = assets_dir / f"{item_id}{ext_of(og_url)}"
            if fetch_og_image(og_url, dest):
                print(f"  ✓ [{idx:>2}/{len(items)}] og:image     {item_id}  → {dest.name}")
                ok_og += 1
                continue

        # X: try tweet media
        if platform in ("x.com", "twitter.com"):
            sub_dir = assets_dir / item_id
            if fetch_x_media(url, sub_dir):
                print(f"  ✓ [{idx:>2}/{len(items)}] x-media      {item_id}  → {sub_dir.name}/")
                ok_x += 1
                continue

        miss += 1
        print(f"  · [{idx:>2}/{len(items)}] miss         {item_id}  ({platform})")

    total = ok_og + ok_x + miss
    print(f"✓ assets: {ok_og} og:image + {ok_x} x-media / {total} ({miss} missing → fallback to SVG)")


if __name__ == "__main__":
    main()

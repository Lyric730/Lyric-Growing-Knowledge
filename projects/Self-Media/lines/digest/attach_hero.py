"""
Step 5: 把 og_fetch 抓到的素材接入 final.json hero.image_url

工作流：
  1. 读 daily/<date>/digest/work/final.json (8 events 选好且撰写完成)
  2. 读 daily/<date>/digest/work/enriched_raw.json (含 url → raw_id 映射)
  3. 对每条 event 按 source.url 查 raw_id，去 work/assets/ 找抓到的图：
       - og:image     work/assets/<raw_id>.<ext>
       - X media      work/assets/<raw_id>/tweets/tweet_*.{jpg,mp4}
  4. 把图复制到 daily/<date>/digest/publish/images/assets/<event-id>.<ext>
  5. 填 final.event.hero.image_url = "images/assets/<event-id>.<ext>"
     抓不到 → 保留 hero.big/sub 不动（fallback 大字）

Usage:
    python lines/digest/attach_hero.py <YYYY-MM-DD>
"""
import argparse
import json
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("date")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = Path(args.root)
    work_dir = root / "daily" / args.date / "digest" / "work"
    publish_dir = root / "daily" / args.date / "digest" / "publish"
    final_path = work_dir / "final.json"
    enriched_path = work_dir / "enriched_raw.json"
    assets_src = work_dir / "assets"
    assets_dst = publish_dir / "images" / "assets"

    if not final_path.exists():
        raise SystemExit(f"missing: {final_path}")
    if not enriched_path.exists():
        raise SystemExit(f"missing: {enriched_path}")

    final = json.loads(final_path.read_text(encoding="utf-8"))
    enriched = json.loads(enriched_path.read_text(encoding="utf-8"))

    # Build url → raw_id map (strip protocol for tolerant matching)
    def norm(u: str) -> str:
        return u.lstrip("/").replace("https://", "").replace("http://", "").rstrip("/")

    url_to_id = {norm(item.get("url", "")): item.get("id") for item in enriched.get("items", [])}

    assets_dst.mkdir(parents=True, exist_ok=True)
    n_image = n_fallback = n_missing = 0

    for event in final.get("events", []):
        url = norm(event.get("source", {}).get("url", ""))
        raw_id = url_to_id.get(url)
        event_id = event.get("id", "event-??")

        copied_path = None
        if raw_id:
            # Try og:image (flat .png/.jpg next to assets/)
            for ext in (".png", ".jpg", ".jpeg", ".webp"):
                candidate = assets_src / f"{raw_id}{ext}"
                if candidate.exists() and candidate.stat().st_size > 1000:
                    dst = assets_dst / f"{event_id}{ext}"
                    shutil.copy2(candidate, dst)
                    copied_path = f"images/assets/{event_id}{ext}"
                    break
            # Try X media (assets/<raw_id>/tweets/tweet_*.{jpg,mp4})
            if not copied_path:
                tweet_dir = assets_src / raw_id / "tweets"
                if tweet_dir.exists():
                    for p in sorted(tweet_dir.iterdir()):
                        if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp") and p.stat().st_size > 1000:
                            dst = assets_dst / f"{event_id}{p.suffix.lower()}"
                            shutil.copy2(p, dst)
                            copied_path = f"images/assets/{event_id}{p.suffix.lower()}"
                            break

        # Update event.hero
        hero = event.setdefault("hero", {})
        if copied_path:
            hero["image_url"] = copied_path
            # Clear fallback big/sub when image present (template prefers image)
            # but keep them as backup commented in JSON — actually just leave them
            n_image += 1
            print(f"  ✓ {event_id}  → {copied_path}  (raw_id={raw_id})")
        elif hero.get("big") or hero.get("sub"):
            n_fallback += 1
            print(f"  · {event_id}  fallback (big={hero.get('big', '')[:20]})")
        else:
            n_missing += 1
            print(f"  ! {event_id}  MISSING (no image and no fallback) — url={url}")

    final_path.write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ attach_hero done: {n_image} image / {n_fallback} fallback / {n_missing} missing")
    print(f"  → final updated: {final_path}")
    print(f"  → images copied: {assets_dst}")


if __name__ == "__main__":
    main()

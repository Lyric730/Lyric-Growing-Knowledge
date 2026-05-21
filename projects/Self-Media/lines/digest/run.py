"""
一键 orchestrator — 跑通日报全链路。

Usage:
    python lines/digest/run.py 2026-05-18                # 默认: 等人工 /digest
    python lines/digest/run.py 2026-05-18 --auto         # 自动调 claude -p /digest（无人值守）
    python lines/digest/run.py 2026-05-18 --skip-fetch   # 跳 fetch
    python lines/digest/run.py 2026-05-18 --skip-enrich  # 跳 enrich
    python lines/digest/run.py 2026-05-18 --only-render  # 仅渲染（final.json 已存在）
    python lines/digest/run.py 2026-05-18 --only-pack    # 仅生成 post.md+README

模式说明:
- 默认: Step 3 停下来等你在 Claude 对话里跑 /digest，按 Enter 继续。
- --auto: Step 3 自动调 `claude -p "/digest <date>"` 跑（用于 cron / Windows 任务计划程序）。
  需要 claude CLI 在 PATH 里。会用 --allowedTools 白名单防卡权限。
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

# 这个脚本在 lines/digest/run.py，向上 3 层是 Self-Media/
ROOT = Path(__file__).resolve().parents[2]
LINE = "digest"
SCRIPT_DIR = "lines/digest"


def run(cmd: list[str], description: str) -> None:
    print(f"\n→ {description}")
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode != 0:
        print(f"  ✗ FAILED (exit {result.returncode})")
        sys.exit(result.returncode)


def file_exists(p: Path, min_bytes: int = 100) -> bool:
    return p.exists() and p.stat().st_size > min_bytes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("date", help="YYYY-MM-DD")
    parser.add_argument("--skip-fetch", action="store_true")
    parser.add_argument("--skip-enrich", action="store_true")
    parser.add_argument("--only-render", action="store_true", help="跳过 fetch/enrich，仅渲染（final.json 已就绪）")
    parser.add_argument("--only-pack", action="store_true", help="仅生成 post.md + README（PNG 已存在）")
    parser.add_argument("--auto", action="store_true", help="无人值守：用 claude -p 自动跑 /digest（替代 input 等待）")
    args = parser.parse_args()

    date = args.date
    work = ROOT / "daily" / date / LINE / "work"
    pub = ROOT / "daily" / date / LINE / "publish"
    raw = work / "raw.json"
    enriched = work / "enriched_raw.json"
    final = work / "final.json"
    daily_html = pub / "daily.html"

    print(f"═══ Digest Pipeline · {date} ═══")

    # ----- Step 1: fetch -----
    if args.only_render or args.only_pack:
        pass
    elif args.skip_fetch and file_exists(raw):
        print(f"\n→ Step 1 fetch: SKIP (--skip-fetch + raw.json 已存在)")
    else:
        run(["python3", f"{SCRIPT_DIR}/fetch_aihot.py", date], "Step 1: fetch_aihot")

    # ----- Step 2: enrich -----
    if args.only_render or args.only_pack:
        pass
    elif args.skip_enrich and file_exists(enriched):
        print(f"\n→ Step 2 enrich: SKIP (--skip-enrich + enriched_raw.json 已存在)")
    else:
        run(["python3", f"{SCRIPT_DIR}/enrich_parallel.py", date], "Step 2: enrich_parallel (耗时 5-10 min)")

    # ----- Step 3: 等 final.json（或 auto 模式跑 claude -p） -----
    if args.only_pack and file_exists(final):
        print(f"\n→ Step 3 final.json: ✓ (--only-pack)")
    elif file_exists(final):
        print(f"\n→ Step 3 final.json: ✓ already exists, skipping /digest")
    elif args.auto:
        print(f"\n→ Step 3 (--auto): 调 claude -p /digest {date}")
        prompt = (
            f"Run the /digest skill for date {date}. Read .claude/commands/digest.md.\n"
            f"\n"
            f"YOUR ONLY JOB: write daily/{date}/digest/work/final.json + run the Pydantic schema validation.\n"
            f"\n"
            f"DO NOT run any of these (run.py handles them after you exit):\n"
            f"  - python3 lines/digest/render_html.py\n"
            f"  - python3 lines/digest/screenshot.py (starts chrome subprocess — hangs in detached cron env)\n"
            f"  - python3 lines/digest/auto_post_md.py\n"
            f"  - python3 lines/digest/auto_readme.py\n"
            f"  - any HTTP server / chrome / long-running process\n"
            f"\n"
            f"After schema validates, print ONE line confirmation and exit. Do not ask permission."
        )
        try:
            subprocess.run(
                [
                    "claude",
                    "-p", prompt,
                    "--allowedTools", "Read Write Edit Bash",
                    "--add-dir", str(ROOT),
                ],
                cwd=str(ROOT),
                check=True,
                timeout=900,  # 15 min hard cap
            )
        except subprocess.TimeoutExpired:
            if file_exists(final):
                print(f"  ⚠ claude -p 超时但 final.json 已就绪，继续")
            else:
                print(f"  ✗ claude -p 超时且 final.json 缺失 (15 min)")
                sys.exit(2)
        except subprocess.CalledProcessError as e:
            if file_exists(final):
                print(f"  ⚠ claude -p 非零退出 ({e.returncode}) 但 final.json 已就绪，继续")
            else:
                print(f"  ✗ claude -p 失败 (exit {e.returncode}) 且 final.json 缺失")
                sys.exit(e.returncode)
        if not file_exists(final):
            print(f"  ✗ claude 跑完但 final.json 不存在 — 检查 digest.md skill 是否报错")
            sys.exit(3)
        print(f"  ✓ final.json 已就绪（自动）")
    else:
        print(f"\n→ Step 3: 等 final.json (人工模式)")
        print(f"  现在去 Claude 对话里跑 `/digest {date}` skill")
        print(f"  期望：{final}")
        print(f"  按 Enter 继续（或 Ctrl-C 中断）...")
        try:
            input()
        except KeyboardInterrupt:
            sys.exit(0)
        if not file_exists(final):
            print(f"  ✗ final.json 仍不存在，退出")
            sys.exit(1)
        print(f"  ✓ final.json 已就绪")

    # ----- Step 4: schema 验证 -----
    run(
        ["python3", "-c",
         f"import sys; sys.path.insert(0, 'lines/digest'); "
         f"from schemas.enriched import Daily; import json; "
         f"Daily.model_validate(json.load(open('{final}'))); print('schema OK')"],
        "Step 4: schema 验证",
    )

    # ----- Step 5: render -----
    if args.only_pack and file_exists(daily_html):
        print(f"\n→ Step 5 render: SKIP (--only-pack + daily.html 已存在)")
    else:
        run(["python3", f"{SCRIPT_DIR}/render_html.py", str(final), str(daily_html)], "Step 5: render_html")

    # ----- Step 6: screenshot 9 PNG -----
    if args.only_pack:
        print(f"\n→ Step 6 screenshot: SKIP (--only-pack)")
    else:
        run(
            ["python3", f"{SCRIPT_DIR}/screenshot.py", str(final), str(daily_html), str(pub / "images")],
            "Step 6: screenshot 9 PNG",
        )

    # ----- Step 7: auto post.md + README -----
    run(
        ["python3", f"{SCRIPT_DIR}/auto_post_md.py", str(final), str(pub / "post.md")],
        "Step 7a: auto_post_md",
    )
    run(
        ["python3", f"{SCRIPT_DIR}/auto_readme.py", str(final), str(pub / "README.md")],
        "Step 7b: auto_readme",
    )

    print(f"\n═══ ✓ DONE — daily/{date}/{LINE}/publish/ ═══")
    print(f"  下一步：")
    print(f"  1. 开 {pub}/post.md 选标题")
    print(f"  2. 浏览器看 http://localhost:8765/daily/{date}/{LINE}/publish/daily.html")
    print(f"  3. 复制 9 PNG 到桌面 → 小红书发布")


if __name__ == "__main__":
    main()

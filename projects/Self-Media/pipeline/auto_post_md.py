"""
从 final.json 渲染 post.md.j2 → publish/post.md

Usage:
    python pipeline/auto_post_md.py <final.json> <output.md>
"""
import argparse
import json
import re
import subprocess
from datetime import datetime, date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = ROOT / "pipeline" / "templates"


def strip_em(s: str) -> str:
    return re.sub(r"</?em>", "", s)


def grep_compliance(text: str) -> list[str]:
    """简单 grep 公司名 / 内部数据敏感词。返回命中列表（空 = 安全）。"""
    sensitive = ["字节跳动", "腾讯内部", "阿里内部", "@team", "内部 PRD", "本周 OKR"]
    return [w for w in sensitive if w in text]


def date_label_cn(d: date) -> str:
    return d.strftime("%Y-%m-%d")


def date_short_cn(d: date) -> str:
    return d.strftime("%-m/%-d")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("final_json")
    parser.add_argument("output_md")
    args = parser.parse_args()

    data = json.loads(Path(args.final_json).read_text(encoding="utf-8"))
    d = date.fromisoformat(data["date"])

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape([]),
        trim_blocks=False,
        lstrip_blocks=False,
    )
    tpl = env.get_template("post.md.j2")

    # 算 post 正文字数（intro 200 + 8 件标题 + outro 60）
    titles_chars = sum(len(e["title"]) + len(e.get("title_tail", "")) for e in data["events"])
    body_chars = 200 + titles_chars + 60

    # 额外标签 — 从分类生成
    cats = sorted({e["category"] for e in data["events"]})
    extra_tags = [c for c in cats if c not in ("Industry",)][:3]

    rendered = tpl.render(
        date=data["date"],
        date_label=date_label_cn(d),
        date_short=date_short_cn(d),
        issue_no=data.get("issue_no_inner", "NO. ???").replace("NO. ", ""),
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        events=data["events"],
        body_chars=body_chars,
        extra_tags=extra_tags,
    )

    # 合规 grep
    hits = grep_compliance(rendered)
    if hits:
        rendered = rendered.replace(
            "**自动 grep check**（生成时已扫过）：未发现敏感词。如手工再改正文，请重 grep。",
            f"**⚠️ 合规警告**：生成时 grep 命中 {hits} — 发布前必须人工处理！",
        )

    out = Path(args.output_md)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered, encoding="utf-8")
    print(f"✓ post.md → {out} ({len(rendered)} chars, compliance hits: {len(hits)})")


if __name__ == "__main__":
    main()

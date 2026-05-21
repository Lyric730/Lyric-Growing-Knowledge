"""
从 final.json 生成 publish/README.md（发布步骤 + 文件清单）

Usage:
    python pipeline/auto_readme.py <final.json> <output.md>
"""
import argparse
import json
import re
from pathlib import Path


def strip_em(s: str) -> str:
    return re.sub(r"</?em>", "", s)


README_TEMPLATE = """# {date} 发布包

> v3.10 排版（→ 报道 / 评论区 / 小刀说 / 本周尝试 + 绿色 em 高光 + 1-8 等权封面）
> 小刀老师直接用，不动其他文件。

## 文件清单

| 文件 | 用途 |
|---|---|
| `post.md` | 小红书发布稿（标题候选 / 正文 / 标签 / 上传顺序 / 合规 checklist）|
| `daily.html` | 浏览器预览（`http://localhost:8765/daily/{date}/publish/daily.html`）|
| `images/01-cover.png` | 封面（上传第 1 张）|
| `images/02-event-01.png` ~ `09-event-08.png` | 8 张事件卡（按顺序上传）|

## 发布步骤

1. **打开 post.md**，从 4 个标题里选 1 个
2. **浏览器开 daily.html** 最终检查（`http://localhost:8765/daily/{date}/publish/daily.html`）
3. **Windows 拿图**：资源管理器 → `\\\\wsl.localhost\\Ubuntu\\home\\lyric\\Making money\\Lyric-Self-Improve\\projects\\Self-Media\\daily\\{date}\\publish\\images\\`
4. **复制 9 张 PNG 到桌面**
5. **小红书 App 发布**：按 01 → 09 顺序上传 → 粘贴 post.md 正文 + 标签 → 发布

## 备份

- `../work/` — pipeline 中间产物（raw.json / enriched_raw.json / final.json）
- `../_archive/` — 开发产物（如有）

## 本期数据

{stats_table}

## v3.10 排版特性

- 每件 4 个 section labels：→ 报道 / 评论区 / 小刀说 / 本周尝试
- 每件 story 350-380 字 / 3 段 / 5-6 处绿色 em 高光
- 每件 2-3 条真实评论（quotes，不假冒第三人）
- 每件 1 句 take（PM 视角狠话）
- 每件 1 个「本周尝试」（actionable 行动）
- 封面 1-8 等权列表（不再金字塔）
- 背景去黄去 grain（chroma 0.005）
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("final_json")
    parser.add_argument("output_md")
    args = parser.parse_args()

    data = json.loads(Path(args.final_json).read_text(encoding="utf-8"))

    # build stats table
    rows = [
        "| # | 标题 | 分类 | story 字 | quotes |",
        "|---|---|---|---:|---:|",
    ]
    for e in data["events"]:
        chars = sum(len(strip_em(p)) for p in e["story_paragraphs"])
        title = e["title"][:25] + ("..." if len(e["title"]) > 25 else "")
        rows.append(f"| {e['rank']:02d} | {title} | {e['category']} | {chars} | {len(e['quotes'])} |")
    stats_table = "\n".join(rows)

    rendered = README_TEMPLATE.format(date=data["date"], stats_table=stats_table)

    out = Path(args.output_md)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered, encoding="utf-8")
    print(f"✓ README.md → {out}")


if __name__ == "__main__":
    main()

"""
Daily AI Digest — enriched data schema v3.0 (Pydantic).

v3 简化 (2026-05-17)：取消 hero 插图，正文/评论/反思撑起视觉。
- Removed: Hero（v2 短命，从未稳定贡献视觉）
- Changed: quote (单条) → quotes: list[Quote] (2-3 条主评+反驳+真实情景)
- Event 卡 reduced to 6 elements: rail / title / story / take / quotes / footer

quotes 视觉权重 (per .impeccable.md v3)：
- 2 条 = 标准 (主评 + 反驳)
- 3 条 = 富文章 (主评 + 反驳 + 真实情景)
- 4+ 条 = 会挤到 16px 字号，避免
"""
from datetime import date
from typing import Optional

from pydantic import BaseModel


# ------- Source / Quote -------

class Source(BaseModel):
    """事件卡 footer URL + (optional) attribution + 热度信号"""
    url: str
    handle: Optional[str] = None
    platform: str = "other"
    likes: Optional[int] = None
    retweets: Optional[int] = None
    replies: Optional[int] = None         # v3.2 加 — 评论区数量
    secondhand: Optional[str] = None


class Quote(BaseModel):
    text: str
    zh: Optional[str] = None
    attr: str


# ------- Event card (v3) -------

class Event(BaseModel):
    id: str                       # "event-01" ... "event-08"
    rank: int                     # 1..8
    category: str                 # "Market", "Workforce", "AI Infra", ...
    title: str
    title_tail: str = ""          # ln-tail after em-dash
    source: Source

    story_paragraphs: list[str]
    take: str                     # 一句话反思（accent 32px，PM 视角狠话，25-40 字）
    quotes: list[Quote]           # 2-3 条 (主评 + 反驳 + optional 真实情景)
    action: Optional[str] = None  # v3.5「本周尝试」: PM 给的 actionable 落地建议 (30-50 字)

    # v3.10 排版优先级规则：当事件卡 1080×1440 装不下所有组件时，
    # action（本周尝试）必须完整显示 > take（小刀说）> quotes（评论）。
    # 实际操作：如果 action 被截或被 footer 重叠，先把 quotes 从 3 条砍到 2 条；
    # 仍不够再砍 story 1 段或 50 字。永远不能砍 action / take / footer。


# ------- Daily (root) -------

class Daily(BaseModel):
    """events 是单一来源 — cover 派生 Top 1/2/3 + TOC。"""
    date: date
    issue_number: str = "VOL. 001"
    issue_no_inner: str = "NO. 001"
    brand_name: str = "小刀的 AI 实验室"
    brand_tagline: str = "a daily AI resonance brief"
    cover_kicker_main: str = "昨日 AI 圈"
    cover_kicker_count: str = "8 件"
    cover_kicker_tail: str = "值得知道的事"
    cover_eyebrow: str = "DAILY EDITION · 昨日要览"
    events: list[Event]

    def total_events(self) -> int:
        return len(self.events)

    @property
    def issue_date_label(self) -> str:
        return self.date.strftime("%b %d · %Y").upper()


if __name__ == "__main__":
    import json

    sample = {"date": "2026-05-12", "events": []}
    daily = Daily.model_validate(sample)
    print(f"OK: {daily.date} ({daily.issue_date_label}) · {daily.total_events()} events")
    print(json.dumps(daily.model_dump(mode="json"), ensure_ascii=False, indent=2)[:200])

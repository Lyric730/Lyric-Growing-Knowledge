# Pipeline 总规划 · 化整为一

> 创建：2026-05-15 · dry-run v1.5 ship 完成后立即梳理
> 单一来源：未来所有 pipeline session 进来先读这份
> Owner：小刀老师（solo-op） · 时间预算 5-10h/周

---

## TL;DR

dry-run v1.5（9 图模板）已 ship 🟡 可用级。
**Pipeline 目标**：每天小刀老师 `/daily 2026-MM-DD` 触发，Claude（我）在对话里跑"判断步骤"+ 调机械脚本，10-15 min 完成 9 图。
**关键架构（2026-05-15 拍板）**：**不用 Claude API**——共鸣预筛/撰写/选 hero/fact check 全部由我在对话里执行，封装成 Claude Code skill。
**关键路径**：模板抽象（Sprint 0）→ 抓取层（Sprint 1）→ Skill 化（Sprint 2，合并原 S2/S3）。
**3 个 Sprint × 5-10h/周 ≈ 2-3 周完成 v1**。

### 5 点决策（2026-05-15）

| # | 选择 | 影响 |
|---|---|---|
| 1 | Jinja2 模板引擎 | 与 Python pipeline 一致 |
| 2 | Pydantic schema | 运行时校验 + IDE 提示 |
| 3 | Sprint 0 用 sample 假数据 | 不动 5/12 真数据 |
| 4 | OpenCLI `twitter screenshot` 直接 spike | 已做：命令为 `twitter download`，progressive fallback |
| 5 | **不用 Claude API，做成 skill 由 Claude 每天执行** | 省 API 成本 / prompt 工程 / LLM ops 复杂度 |

---

## A. 已有资产盘点（dry-run v1.5 ship 完成）

### A.1 视觉层 — `daily/2026-05-12/preview/dry-run.html`

**Design tokens**
- OKLCH 颜色：`--ink` 深色油墨 / `--cream` newsprint / `--accent` 墨绿 `oklch(0.42 0.085 158)`
- 字体栈：LXGW WenKai (CDN jsdelivr) · Noto Serif SC · Bricolage Grotesque · PT Mono · PT Serif
- 4pt spacing scale：`--s-1` to `--s-8`

**封面组件**
- `.masthead` 刊头 + 卷期号 / `.cover-kicker` 132px display / `.cover-top-event` Top 1 / `.cover-tops23` Top 2/3 双联

**事件卡组件**（v1.5 模板骨架，铁律 8 段）
1. `.card-rail` — 栏目标签 + 序号
2. `.event-tags` — 来源 + Letterpress 标签（B 样式 tint bg + inset shadow）
3. `.card-title` + `.ln-tail` — 共鸣化标题（4 条钩子纪律）
4. `.card-hero` — **6 种 hero-art swap**（详 A.2）
5. `.card-body` 双栏：`.card-story` + `.card-side` (5 种 data-points swap)
6. `.card-take` — 跨全宽个人观点（raw 口语）
7. `.card-quote` — 评论区高赞引用
8. `.card-footer` — URL + brand

**通用**
- `.slide` 1080×1440 + `overflow: hidden` + `:target` focus mode（CSS-only，零 JS）
- `.grain-dark` / `.grain-light` 网点纹理
- `.event-tag` / `.event-tag.tag-hot` Letterpress 风

### A.2 6 种 hero-art swap（按事件类型）

| Hero 类型 | CSS class | 5/12 用例 |
|---|---|---|
| SVG 数据可视化 | `.hero-fact` + 内嵌 SVG | event-01 投资 $225M→$5.5B 横条图 |
| 大数字 callout | `.hero-callout` | event-03 80% / event-04 200K+ / event-08 月→小时 |
| 产品关键词 | `.hero-keyword` | event-05 Likeness / event-06 200ms |
| 双值对比 | `.hero-vs` | event-02 6/2 vs 5/12 |
| 2 方对峙 | `.hero-dueling` | event-07 山姆 vs 埃隆 + 印章 |
| 推文 raw 引用 | `.hero-excerpt` | （备用，dry-run 未用）|

### A.3 5 种 data-points swap（body 右栏）

`The Numbers` / `The Bets` / `The Specs` / `The Stakeholders` / `The Timeline`

### A.4 规范层
- `CLAUDE.md` — 项目宪法 + WSL 环境约定
- `.impeccable.md` — Design Context（Users / Brand / Aesthetic / Principles / 钩子纪律 / v1.5 组件 spec / Anti-references）

### A.5 工具栈（实测状态）

| 工具 | 用途 | 状态 |
|---|---|---|
| aihot.virxact.com API | mode=all 抓 30-50 候选 | 🟢 实测过 |
| OpenCLI `twitter thread` | X 精读 + 评论区 | 🟢 实测过 |
| WebFetch | 非 X 链接精读 | 🟢 |
| curl + grep og:image | 文章封面图 | 🟡 spike 通过（per-source 不可靠）|
| google-chrome --headless 1080×1440 | HTML→PNG | 🟢 实测过（`:target` URL hash）|
| Claude API | 共鸣化撰写 + 评分 | 🔴 未集成 |
| OpenCLI `twitter screenshot` | 原推 media 抓取 | 🔴 未实测 |

---

## B. Gap 清单（pipeline 要补的）

### B.1 数据层 schema 未定义

需要：
- `daily/<date>/raw.json` — aihot 原始抓取
- `daily/<date>/enriched.json` — 精读后结构化数据
- `daily/<date>/final.json` — 共鸣化撰写完成 + hero_type 已决策

**enriched.json schema 草案**（每条事件）：
```json
{
  "id": "event-NN",
  "rank": 1,
  "category": "market | workforce | ai-infra | security | product | ai-models | industry",
  "source": {
    "url": "...",
    "handle": "@kimmonismus",
    "platform": "x | the-decoder | ithome | ...",
    "interactions": { "likes": 855, "retweets": 55 },
    "secondhand": "FT"
  },
  "title": "OpenAI 解雇的那个人，用 12 个月把 2.25 亿做成 55 亿——但评论区一眼算清账",
  "story_paragraphs": ["...", "...", "..."],
  "hero": {
    "type": "svg | callout | keyword | vs | dueling | excerpt",
    "data": { /* 按 type 不同 */ }
  },
  "data_points": {
    "type": "numbers | bets | specs | stakeholders | timeline",
    "items": [ /* 按 type 不同 */ ]
  },
  "take": "讲得像 AI 洞察，其实是赌对了能源紧缺周期。运气+故事=24倍，普通人复制不来。",
  "quote": {
    "text": "...",
    "zh": "...",
    "attr": "@tizimmer · 评论区原文"
  },
  "assets": {
    "hero_image_url": null  // pipeline 抓到才填，否则 fallback 到 SVG/CSS hero
  }
}
```

### B.2 模板抽象（最关键 gap）

当前 dry-run.html **1500+ 行死数据**。要变 pipeline-friendly 模板：
- 选 Jinja2（Python）或 Nunjucks（Node）模板引擎
- 6 种 hero `{% if hero.type == 'callout' %}...{% elif ... %}` 切换块
- 5 种 data-points 同模式
- 数据驱动 SVG（hero-fact 的 bar chart 宽度从变量计算）
- 封面 Top 1/2/3 从 enriched.json 自动挑选 + 渲染

### B.3 机械步骤脚本（Python，无 LLM 依赖）

| 文件 | 用途 | 依赖 |
|---|---|---|
| `pipeline/fetch_aihot.py` | Step 1 抓 aihot API → raw.json | requests |
| `pipeline/enrich_parallel.py` | Step 3 并行精读（X 用 OpenCLI / 非 X 用 WebFetch）→ enriched_raw.json | subprocess |
| `pipeline/og_fetch.py` | 抓 hero 素材（og:image / 推文 media，抓不到不报错）| curl + grep |
| `pipeline/render_html.py` | Step 6 Jinja2 模板渲染 → daily.html | jinja2 + pydantic |
| `pipeline/screenshot.py` | Step 6 chrome headless 1080×1440 → 9 PNG | subprocess |

### B.4 判断步骤（由 Claude 在对话里执行）

不写脚本，写进 skill 文档：

- **Step 2 共鸣预筛**：读 raw.json → 按 P0/P1 共鸣强度打分 → 选 top 15（依据：标题里数字/对比/反钩 hint 强度）
- **Step 4 评论区反驳扫描**：读 enriched_raw.json → 扫每条评论区高赞反驳 → 删除"故事被一眼算清账"的可疑条目
- **Step 5 共鸣化撰写**：按 [[钩子纪律]]4 条 → 改写标题 + story_paragraphs + take（保留 raw 口语）
- **Step 5+ 选 hero 类型**：6 种 hero 按事件类型 swap（见 [[hero-types]]）+ 填 hero.data 字段
- **Step 7 post.md 生成**：小红书发布文案 + 标签 + 互动钩子（评论区埋问题）

### B.5 Skill 层（要写）

主入口：`.claude/commands/daily.md`（项目级 slash command，输入 `/daily 2026-05-15` 触发）

内容应包含：
- 7 步 workflow 主流程
- 6 种 hero 类型决策树
- 4 条钩子纪律 datasheet
- 评论区 fact check 方法
- 小红书 post.md 模板
- 失败兜底（哪些步骤抓不到时该怎么 fallback）
- 在职合规检查清单（公司名 / 内部数据红线）

### B.6 配置层

- `pipeline/config.yaml` — aihot endpoint / OpenCLI daemon URL / 输出路径
- 无需 `.env`（不依赖 Claude API key）

---

## C. Sprint 拆解（3 周节奏，按依赖排）

### Sprint 0 — 模板抽象（W1，3-5h）

**目标**：把 dry-run.html 改造成 Jinja2 模板，能用 enriched.json 一键填充生成 9 张图。

任务：
1. 把 dry-run.html 拆 → `pipeline/templates/daily.html.j2`
2. 6 种 hero / 5 种 data-points 切换块
3. 定义 `enriched.json` schema（Pydantic 推荐）
4. 写 `pipeline/render_html.py`（CLI：`python render_html.py enriched.json output.html`）
5. 写 `pipeline/screenshot.py`（HTML → 9 PNG）
6. **验收**：手填一份 enriched.json，跑两个脚本，复现 dry-run 9 张图

**产出**：`templates/daily.html.j2` + `render_html.py` + `screenshot.py` + sample enriched.json

### Sprint 1 — 抓取层（W2，5-7h）— 进行中 🟡

**目标**：从 aihot API 跑到 enriched_raw.json（含原始数据 + 抓到的 hero 素材）。

任务：
1. ✅ `fetch_aihot.py` — `python fetch_aihot.py 2026-05-15 --take 100` → work/raw.json（5/15 实测 100 条候选）
   - 已知 limitation：API 忽略 since/until，总返回最近 N 条 desc。TODO：nextCursor 分页拉前一天
2. ✅ `enrich_parallel.py` — X 用 OpenCLI `twitter thread` / 非 X 用 requests+og:meta → work/enriched_raw.json
   - 5/15 6 条 smoke test：5 X / 1 article，0 errors
3. 🟡 `og_fetch.py` — og:image + OpenCLI `twitter download` → work/assets/（运行中）
4. ⬜ CSS filter 印刷化处理 spec（fold 进 daily.html.j2 模板）
5. **验收**：跑一键脚本，今日出 enriched_raw.json，30-50 条原始 + 部分 hero 素材

**产出（截至 5/15）**：`fetch_aihot.py` + `enrich_parallel.py` + `og_fetch.py`

### 新增：每日发布包目录结构（2026-05-15 拍板）

每天产物按"发布包/中间产物/归档"三段分：

```
daily/<YYYY-MM-DD>/
├── publish/              ← 小刀直接用的发布包
│   ├── README.md         使用说明
│   ├── post.md           小红书发布稿（标题/正文/标签/合规清单）
│   ├── daily.html        浏览器预览（http://localhost:8765/daily/.../publish/daily.html）
│   └── images/           9 张 1080×1440 PNG（01-cover.png .. 09-event-08.png）
├── work/                 ← pipeline 中间产物
│   ├── raw.json          aihot 原始抓取
│   ├── enriched_raw.json 精读后
│   ├── final.json        撰写完成（喂 Jinja2 模板）
│   └── assets/           抓到的 hero 素材（og:image / 推文 media）
└── _archive/             ← 开发过程产物（dry-run / tag-gallery / 旧版图）
```

### Sprint 2 — Skill 化 + 编排（W3，5-7h）

**目标**：把"我每天执行"的判断步骤封装成 `.claude/commands/daily.md`，加机械步骤 wrapper，串通 e2e。

任务：
1. 写 `.claude/commands/daily.md` 主入口
   - 7 步 workflow（机械/判断标注清楚）
   - 6 种 hero 类型决策树
   - 4 条钩子纪律 datasheet
   - 评论区 fact check 方法
   - 在职合规检查清单（公司名 / 内部数据红线）
2. 写 `pipeline/run.py` 机械步骤 wrapper（串 fetch + enrich + render + screenshot）
3. 写 `templates/post.md.j2` 小红书发布文案模板
4. 写 `REVIEW_CHECKLIST.md` 小刀老师 10-15 min review 流程
5. 走通 e2e：`/daily 2026-05-NN` → 我执行判断 → 调 `run.py` 跑机械步骤 → 出 9 PNG + post.md
6. **验收**：连续 3 天 e2e 跑通，每天人工时间 ≤ 15 min

**产出**：`.claude/commands/daily.md` + `run.py` + `post.md.j2` + `REVIEW_CHECKLIST.md`

---

## D. 风险清单（提前知道才能 ship 前避坑）

| 风险 | 等级 | 影响 | 缓解 |
|---|---|---|---|
| Claude（我）每天判断步骤不一致 | 🐛 中 | 标题/钩子飘移 | skill 文档加严格 datasheet + 钩子纪律 4 条；每周人工抽检一致性 |
| OpenCLI daemon 触发不稳 | 🐛 中 | 抓取失败 | 抓不到不报错（fallback）+ skill 里加"重跑 enrich"指令 |
| aihot API beta schema 变动 | 🗑 中 | 解析报错 | 解析层加 schema validation + 错误日志 |
| og:image / 推文 media 抓取不可靠 | 🐛 中 | hero 区无图 | progressive enhancement：抓不到 fallback 到 SVG/CSS hero |
| Jinja2 6×5=30 种 hero/dp 组合崩 | 🐛 中 | 渲染失败 | 模板加 default 块 + sample JSON 测全部组合 |
| 字体 jsdelivr CDN 国内访问慢 | 🐛 低 | 渲染时间长 | 本地化字体 + chrome `--virtual-time-budget` |
| slide overflow: hidden 截内容 | 🐛 中 | footer 被截 | Sprint 0 模板加内容长度 sanity check |
| 在职合规（公司名 / 内部数据）| 🔑 高 | 法律风险 | resonance_write.py prompt 加合规检查 + 人工 review 双保险 |

---

## E. 决策点（已全部拍板 2026-05-15）

1. ✅ Jinja2
2. ✅ Pydantic
3. ✅ Sprint 0 用 sample 假数据
4. ✅ OpenCLI 直接 spike — 已做：命令是 `twitter download`（非 screenshot），纯文字推文返回 "No media found"，对带 media 推文应能下载（未在真带图推文上验证）。pipeline 策略：尝试 download → 抓不到 fallback 到 SVG/CSS hero
5. ✅ **不用 Claude API**——做成 skill 由 Claude 在对话里执行

---

## F. 项目结构（pipeline ship 完后）

```
Self-Media/
├── CLAUDE.md
├── .impeccable.md
├── archive/
├── .claude/
│   └── commands/
│       └── daily.md               【关键】skill 入口 — `/daily 2026-05-15` 触发
├── pipeline/
│   ├── PLAN.md                    本文件
│   ├── config.yaml
│   ├── run.py                     机械步骤 wrapper（fetch → enrich → render → screenshot）
│   ├── fetch_aihot.py             Step 1 抓 aihot
│   ├── enrich_parallel.py         Step 3 X/非 X 分流精读
│   ├── og_fetch.py                Step 3 附加 — 抓 hero 素材
│   ├── render_html.py             Step 6 Jinja2 渲染
│   ├── screenshot.py              Step 6 chrome headless
│   ├── templates/
│   │   ├── daily.html.j2          1080×1440 9 图模板
│   │   └── post.md.j2             小红书文案模板
│   ├── schemas/
│   │   └── enriched.py            Pydantic models
│   └── fixtures/
│       └── sample_enriched.json   Sprint 0 假数据
├── daily/
│   └── <YYYY-MM-DD>/
│       ├── raw.json               aihot 原始
│       ├── enriched_raw.json      精读后（脚本产出）
│       ├── final.json             撰写完成（我产出）
│       ├── pipeline.log
│       ├── assets/                抓的 hero 素材
│       │   ├── event-01-hero.png
│       │   └── ...
│       ├── preview/
│       │   └── daily.html         Jinja2 渲染输出
│       ├── images/                9 张 PNG（发布素材）
│       │   ├── 01-cover.png
│       │   └── 02-event-01.png ... 09-event-08.png
│       └── post.md                可粘贴小红书的文案
└── REVIEW_CHECKLIST.md            每日 review 流程（10-15 min）
```

---

## G. 当前 Next Step

**Sprint 0 启动前**（一次性）：
- [ ] 装 Python deps：`pip install jinja2 pydantic requests pyyaml`
- [ ] 不需要 `.env`（不依赖 Claude API）

**Sprint 0 任务清单**（即将进行）：
- [ ] dry-run.html 1500 行 → daily.html.j2（拆 6 hero / 5 dp 切换块）
- [ ] schemas/enriched.py Pydantic models
- [ ] fixtures/sample_enriched.json sample 假数据
- [ ] render_html.py + screenshot.py
- [ ] 验收：跑 sample → 出 9 PNG 复现 dry-run

---

## H. 三段式收尾（dry-run v1.5 阶段总结）

**ship 了啥**：
- 🟡 9 图模板（封面 + 8 事件卡）v1.5，含 6 种 hero-art swap
- 🟡 .impeccable.md Design Context（钩子纪律 + 组件结构）
- 🟢 工具栈实测（aihot / OpenCLI / chrome headless / WebFetch / og 抓取 spike）
- 🟢 项目宪法 CLAUDE.md + WSL 环境约定

**学了啥**：
- CSS `:target` + `:has()` 是 JS-free focus mode 正解
- chrome headless `--window-size=1080,1440` 真分辨率渲染
- hero-art slot 不是装饰位是"视觉放大镜"——把标题钩子放大 100-140px
- 印章式倾斜小标签是低成本 raw zine 质感来源
- WSL 直接读 `/mnt/c/` 访问 Windows 文件
- og:image 抓取 per-source 不可靠 → 必须做 fallback

**隐忧**：
- 9 张 slide overflow: hidden 风险未逐一确认（footer 可能被截）
- 字体 jsdelivr CDN 国内访问稳定性未测
- Claude API 月成本未估算
- 在职合规防护（公司名 / 内部数据）还没写进 pipeline
- pipeline 的核心成本是 Claude API + OpenCLI daemon 24/7 维护——这两个 solo-op 都没经验

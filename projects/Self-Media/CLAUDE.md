# Self-Media · 项目宪法

> 小刀老师的自媒体 AI 增长 PM 内容项目。
> 这个文件是项目入口——任何 Claude / Agent 进入这个目录工作前，**先读这个文件**。
> 由 `/impeccable teach` 于 2026-05-13 创建并维护与 `.impeccable.md` 的 Design Context 同步。

---

## ⏰ 时间 + 分支确认（每次对话第一步）

**进入对话第一时间跑两条命令**：

```bash
date '+%Y-%m-%d %H:%M:%S %A'   # 真实时间（不信 system currentDate，被观察到偏差 1+ 天）
git -C "/home/lyric/Making money/Lyric-Self-Improve" branch --show-current
```

**branch 必须是 `projects/self-media`**——做 Self-Media 工作前如果在别的分支 (huoshanbei / main)，先 `git checkout projects/self-media`。

**已踩坑**：
- 5/20 我把 5/21 的日报当成 5/20 处理（信 currentDate 没跑 date）
- 5/12 - 5/21 整整 9 天工作在 huoshanbei 分支 untracked，硬盘坏可能全丢（5/21 才发现 commit + push 进 projects/self-media）

---

## 项目定位

在职 AI 增长 PM 的自媒体项目。

- **首要目标**：学习副产物 + 个人品牌/影响力（**不求变现**，Q1 目标）
- **主战场**：小红书图文为主，抖音二刷分发
- **核心定位**：用 PM 视角看穿——AI 工具值不值 / AI 时代怎么转 / AI 怎么落地
- **时间预算**：5-10h/周（自动化后回到该预算内）

---

## 项目结构（多产线架构 · 2026-05-21 重组）

**核心原则**：每条内容产线 = 一个独立 `lines/<name>/` 子目录，自带代码 / 模板 / 视觉 brief / 审稿 DoD。**产线之间不共享设计资产**（人群定位、aesthetic、字体色彩各自独立）。

```
Self-Media/
├── CLAUDE.md                    项目宪法（本文件，入口；跨产线）
├── topics/                      孤立长图文 / 单篇深度（未来可能演化成新产线）
│
├── lines/                       ← 所有内容产线代码 + 资产
│   └── digest/                  ← 产线 1：AI 日报（共鸣速览）
│       ├── PLAN.md              产线总规划
│       ├── REVIEW_CHECKLIST.md  人工审稿 10-15 min DoD
│       ├── .impeccable.md       digest 产线专属视觉 brief
│       ├── archive/             digest 产线归档（定位 design 等）
│       ├── run.py               orchestrator (7 步全链路)
│       ├── scheduled_daily.sh   Windows 任务 → WSL bash 入口
│       ├── send_notify.py       Gmail 邮件通知（含 11 附件）
│       ├── fetch_aihot.py       Step 1 抓 aihot API
│       ├── enrich_parallel.py   Step 2 X/非 X 分流精读
│       ├── og_fetch.py          抓 hero 素材
│       ├── attach_hero.py       hero 素材接入
│       ├── render_html.py       Jinja2 渲染
│       ├── screenshot.py        chrome headless 1080×1440 PNG
│       ├── auto_post_md.py      生成 publish/post.md
│       ├── auto_readme.py       生成 publish/README.md
│       ├── dev.sh               本地预览（render + serve）
│       ├── setup_windows_task.ps1  注册定时任务
│       ├── schemas/enriched.py  Pydantic Daily/Event 模型
│       ├── templates/           Jinja2 模板（daily.html.j2 + post.md.j2）
│       └── fixtures/sample_enriched.json
│
├── .claude/commands/            ← Slash 命令（产线名一致）
│   └── digest.md                /digest skill — digest 产线撰写
│
└── daily/<YYYY-MM-DD>/          ← 产物按日期 + 产线双重隔离
    └── <line-name>/             （目前只有 digest，未来 e.g. weekly/）
        ├── publish/             发布包（直接用）
        │   ├── README.md / post.md / daily.html / images/01-09.png
        ├── work/                pipeline 中间产物（raw / enriched / final.json）
        └── .scheduled-state     定时任务执行状态
```

每天发布工作流：
1. **自动**：Windows 任务 12:00 触发 → wsl bash → `lines/digest/scheduled_daily.sh` → 全链路 + 邮件到 Gmail
2. **手工**：`python3 lines/digest/run.py YYYY-MM-DD --only-render`（已有 final.json 时只补 PNG）
3. 收 Gmail 邮件预览 → 复制 9 PNG 到桌面 → 小红书发

---

## 新增产线规则（重要）

未来加新产线（如 weekly / deep-piece / video-script）的硬约束：

1. **新建独立 `lines/<new-name>/` 目录**，**不复用 digest 的代码 / 模板 / 视觉**
2. **新建独立 `lines/<new-name>/.impeccable.md`**，重新做视觉 brief（人群、aesthetic、字体、色彩）
3. **新建独立 `.claude/commands/<new-name>.md`** slash command
4. **产物落 `daily/<date>/<new-name>/`**，和 digest 物理隔离
5. CLAUDE.md 这份项目宪法仍是跨产线唯一入口；如果产线间发生冲突，分别在 `lines/<name>/PLAN.md` 解决

---

## 关键文档指引

| 文档 | 内容 | 何时看 |
|---|---|---|
| 本文件 | 项目宪法 + 多产线结构 + Design Context 镜像 | 进入项目第一时间读 |
| `lines/digest/archive/2026-05-12-self-media-ai-positioning-design.md` | digest 产线主 design：受众三层、内容支柱、90 天节奏 | digest 策略决策前 |
| `lines/digest/.impeccable.md` | digest 产线视觉 brief（**仅本产线复用，新产线必须独立 brief**）| digest 视觉动作前；`/impeccable craft` 加载 |
| `lines/digest/PLAN.md` | digest pipeline 工程规划 | digest 改架构前 |
| `lines/digest/REVIEW_CHECKLIST.md` | digest 人工审稿 DoD | 每期发布前 10-15 min |
| `.claude/commands/digest.md` | `/digest <date>` skill — Claude 撰写 final.json | 跑 /digest 时自动加载 |

---

## 主形态（2026-05-13 决策更新）

原 design §5 "支柱 ④ AI 新闻 = 10% 调味料" **已升级为主形态**：

| 支柱 | 形态 | 频率 | 优先级 |
|---|---|---|---|
| ④ **AI 共鸣速览**（升级主形态）| 日更聚合：封面 + 8 事件卡（共 9 图）| 5-7 条/周 | 最高 |
| ① AI 职场/转型 | 事件深度图文 | 约 0.8 条/周（保 40% 比例）| 中 |
| ② AI 反 AI 文盲科普 | 事件深度图文 | 约 0.6 条/周（30%）| 中 |
| ③ AI 工具拆解 | 事件深度图文 | 约 0.4 条/周（20%）| 中 |

**差异化锚点**：每条热点用 "P0/P1 共鸣化撰写"（"对你/我意味着什么"）vs 量子位的客观叙述。

---

## Pipeline 架构（W0 待 ship）

```
[Cron 06:00 daily]
    ↓
[1. 抓取]      aihot API mode=all + since=昨日 → 30-50 候选
    ↓
[2. 共鸣预筛]  Claude API + P0/P1 共鸣一问 → top 15
    ↓
[3. 并行精读]  X 链接 → opencli twitter thread (含评论区)
              非 X 链接 → WebFetch
    ↓
[4. 事实核验]  扫评论区高赞反驳 → 过滤可疑条目
    ↓
[5. 共鸣化撰写] Claude API: resonance_title + why_it_matters + one_line_take
    ↓
[6. HTML PPT]  craft 模板渲染 → 9 张 PNG
    ↓
[7. 落盘]      daily/<date>/...
    ↓
[8. 人工审核]  10-15 min 改钩子标题（差异化战场）
    ↓
[9. 发布]      手动 → 后期接自动发布 Agent
```

**人工时间**：仅 Step 8（10-15 min/天）。**自动化是 solo-op 的核心杠杆**。

---

## 工具栈（已验证可用）

| 工具 | 用途 | 状态 |
|---|---|---|
| aihot.virxact.com API | 信源聚合（mode=all 拉原始流） | 🟢 已实测 |
| OpenCLI (`opencli twitter thread`) | X 推文精读 + 评论区抓取（绕过 X 402）| 🟢 已实测，daemon + extension 连通 |
| WebFetch（Claude Code 内置）| 非 X 链接精读 | 🟢 |
| Claude API | 共鸣化撰写 + 评分 prompt | 待集成 |
| Claude HTML PPT | 9 图渲染 | craft 阶段产出 |

---

## 环境约定（WSL）

**Windows 路径访问**：所有 `C:\...` 路径在 WSL 里通过 `/mnt/c/...` 前缀直接读，**不要再说"读不到 Windows 路径"**。
- 用户 Windows 用户名：`26898`
- 常用系统截图位置（Win+Shift+S 截图工具）：`/mnt/c/Users/26898/AppData/Local/Packages/MicrosoftWindows.Client.CBS_cw5n1h2txyewy/TempState/ScreenClip/`
- 用户桌面/文档：`/mnt/c/Users/26898/Desktop/` 与 `/mnt/c/Users/26898/Documents/`
- 用户贴 `C:\Users\26898\...` 路径时直接转 `/mnt/c/Users/26898/...`，用 Read 工具读图，不要"我无法访问"

---

## 创作纪律（不可妥协的红线）

按主 design §5.3 / §7.2 / §10.3：

1. **明确不做**：纯 AI 科普 / 纯新闻搬运 / 泛个人成长鸡汤 / 大模型技术深度
2. **HTML PPT 三纪律**：强设计系统 / 人感调味 / 钩子结构
3. **在职合规**：不暴露公司名、不发内部数据、起步用昵称 + 插画头像
4. **质量门**：DoD 5 项不过 → 不发布，不为凑节奏发不达标内容

---

## Design Context

> 镜像 `.impeccable.md` 的同名 section。两份文件保持同步，单一来源为 `.impeccable.md`。

### Users

- **P0**：大学生迷茫求职（20-25 岁）— 最大流量入口，碎片化阅读，3 秒决定划走
- **P1**：25-30 职场普通人 — AI 时代焦虑、真实变现层、看完要能答"那又怎样"
- **P2**：互联网同行 — 数量小但单粉价值高，对内容深度敏感

**使用场景**：小红书图文流，手机竖屏，碎片时间（白天 60% / 晚间 40%）。

**Job to be done**：每天 3-5 分钟，听一个内行 PM 朋友 simulcast 昨日 AI 圈值得知道的事——要他的判断，不是客观叙述。

### Brand Personality

**Opinionated · Unpolished · Personal**

- **Opinionated 有立场** — PM 视角的内行判断，敢说"这事 80% 是 timing + good story"
- **Unpolished 不端着** — 朴素第一人称，不通顺化的口语感
- **Personal 第一人称在场** — "一句观点"字段必须保留个人口吻，反 AI 矩阵号识别的核心防线

**绝对不是**：客观新闻播报 / 知识付费"震惊体" / AI 工具博主"干货总结" / 人设 vlog

### Aesthetic Direction

**Editorial × Raw Zine** — 杂志结构感 × 独立小报粗粒质感（融合而非二选一）。

- **印刷感 > 数码感**：offset 油墨、网点纹理、RISO 色阶、letterpress 微错位
- **杂志/小报结构**：卷期号、刊头、栏目标记、版权小字、目录页式封面、引文样式
- **沉稳排印**：单一暖/冷色 accent（油墨红/墨绿/砖红/褪色蓝），不要霓虹、不要渐变
- **粗粒质感**：标题略错位、横线略斜——但整体仍要可读

**Theme**：深浅混合
- 封面 + 头条事件：深色 tinted（绝不纯黑）
- 普通事件卡：newsprint cream（绝不纯白）

**字体方向**（craft 阶段实测）：
- 中文 display：霞鹜文楷 / 朱雀仿宋
- 中文 body：寒蝉正楷 / 方正聚珍新仿
- 英文：PT Mono / Söhne Mono / Pitch Sans（避开 Inter / 思源黑体等 reflex）

### Design Principles

1. **印刷品 > 数码产品** — SaaS / 玻璃 / 霓虹深背 = 立即重写
2. **第一人称在场不通顺化** — "一句观点"字段保留 raw 口语
3. **杂志结构 > emoji 装饰** — 用印刷品惯例，不用 emoji / 几何抽象
4. **沉稳排印 > 高对比霓虹** — 单一 accent，60-30-10 视觉权重
5. **节奏感 > 模板化** — 9 图密疏交替，但骨架一致

### Anti-References

- ❌ 量子位 / 机器之心日报（横幅 + 客观叙述 + 调性金黄/青）
- ❌ 小红书白底大字 AI 博主（白底 + emoji + 渐变色块）
- ❌ 知识付费 / 倍股博主（金黄渐变 + "震惊" 词汇）
- ❌ AI 高级感模板造（玻璃 + 霓虹深背 + 渐变文字 + 几何 emoji）

### Aesthetic Preset

**none / custom** — neo-skeuomorphic 对 editorial 方向 explicitly wrong。

---

## Next Steps

- [ ] `/impeccable craft` 产出 5月12 9 图模板 v1（封面 + 1 张事件卡 dry run）
- [ ] W0 准备周清单（design §11 sect）
- [ ] Pipeline Step 1-6 spike 脚本（Python 或 Node，复用 OpenCLI + Claude API）
- [ ] HTML PPT 设计系统 prompt v1

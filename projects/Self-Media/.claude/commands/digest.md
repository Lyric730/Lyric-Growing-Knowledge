---
name: digest
description: 生成当日 AI 日报（digest 产线）的撰写部分 — 从 enriched_raw.json 共鸣化撰写 + 写出 final.json（schema 验证后立即退出，渲染/截图/发布包由外层 run.py 接管）
---

# /digest — AI 日报当日生成

**触发示例**：
- `/digest 2026-05-18` — 指定日期
- `/digest` — 默认今天

**输出**：
- `daily/<date>/digest/work/final.json`（schema 验证过）
- `daily/<date>/digest/publish/daily.html`
- `daily/<date>/digest/publish/images/01-09.png`（9 张 1080×1440）
- `daily/<date>/digest/publish/post.md`（小红书发布稿）
- `daily/<date>/digest/publish/README.md`（发布步骤）

---

## 执行流程（7 步）

### Step 1 — 数据准备
```bash
DATE=<arg-or-today>
ls daily/$DATE/digest/work/enriched_raw.json
```

如果 `enriched_raw.json` 不存在：
1. 跑 `python3 lines/digest/fetch_aihot.py $DATE` 拿 raw.json
2. 跑 `python3 lines/digest/enrich_parallel.py $DATE`（耗时 5-10 min，后台跑）

如果已存在：直接进 Step 2。

### Step 2 — 读 enriched_raw 全部候选
读 `daily/$DATE/digest/work/enriched_raw.json`，把 `items[]` 的关键字段全部列出来：
- title
- source_type (article / x)
- url
- summary
- tweet_likes / tweet_retweets / top_replies（如果是 X）
- body_excerpt（如果是 article）

### Step 3 — 按规则选 8 件

**比例**（按 design context §5）：
- ① **AI 职场 / 转型**（40% = 3 件）— 求职、毕业、晋升、转岗、被替代焦虑
- ② **反 AI 文盲科普**（30% = 2-3 件）— 真实工作流、技术常识、辟谣
- ③ **AI 工具拆解**（20% = 1-2 件）— 真有用的工具或重大产品
- ④ **趣味/调味**（10% = 1 件）— 行业八卦、有梗

**共鸣优先级**（每条问一次）：
1. **P0 大学生迷茫求职**（20-25）— 这件事跟「我快毕业了 / 我要找工作 / AI 抢我饭碗」相关？
2. **P1 25-30 职场普通人**——「AI 时代我该怎么活 / 我的岗位还在不在」相关？
3. **P2 互联网同行** — 行业判断有增量？

至少 **P0 + P1 命中 1 条**才能选。

**强制排除**：
- ❌ 纯论文 / benchmark 评测（陶哲轩这种「顶级专家说话」例外）
- ❌ 单纯产品发布（除非有 P0/P1 共鸣点）
- ❌ 政治 / 八卦 / 汽车 / 美妆 / 不相关行业
- ❌ 你自己当前公司任何提及 — **在职合规红线**

**在职合规 grep check**（无例外）：
- 不出现公司名（小刀当前任职的字节 / 腾讯 / 阿里等任何具体名 — 实际你不会发自己公司的事，但 grep 防漏）
- 不出现公司内部数据 / 决策 / 工具 / 同事名
- 行业通用观察、对外公开信息、个人观点 ✓

**结果**：8 件 + 排序（rank 1-8，Top 1 共鸣最强）。

### Step 4 — 每件共鸣化撰写

**Schema**（Pydantic 验证）：`lines/digest/schemas/enriched.py` Event

每件填：

#### 4.1 title + title_tail
- `title`：钩子标题（人名必带身份「菲尔兹奖得主陶哲轩」「谷歌前 CEO 施密特」），15-25 字
- `title_tail`：「——后半段」补充背景或冲突，10-20 字

#### 4.2 source（沿用 enriched_raw）
- url / handle / platform / secondhand
- likes / retweets / replies（X 数据直接抄）

#### 4.3 story_paragraphs（3 段，≥ 350 字总）
- **段 1**：事实 / 事件（什么发生了 + 关键数据/原文引语 + 当事人身份背景）
- **段 2**：背景 / 转折（为啥这样 + 对比 + 评论区争议 / 反驳）
- **段 3**：「对你/我意味着什么」(P0/P1 共鸣落地)

**每段 100-150 字**，总 350-400 字。

**em 高光规则**：每段 1-2 处 `<em>关键词</em>`，全文共 5-6 处。挑：
- 数字（"50%"、"半数美国人"、"24 倍"）
- 锋利判断词（"在情理之中"、"被替代的第一批"、"账单从工资栏挪到 API 栏"）
- 关键概念（"中间地带"、"母语层级"、"任务级别"）

**字号 26px 装下规则**（v3.10）：每件 ≤ 380 字。超 380 必爆。

#### 4.4 take（一句话 25-40 字，PM 视角狠话）
特征：
- **不说理 / 不解释** — 直接判断
- **带反差** — "X 不是 A，是 B"
- **PM 第一视角** — 用「我」「你」不要「大家」

例：
- "AI 焦虑不需要被「劝」，需要被「接住」。劝你拥抱 AI 的人，自己最不需要拥抱。"
- "稳定工作不是安全垫，是慢性丧失感的来源。真安全是「我每天还在筛选、还在被现实验证」。"
- "「软件免费」是 CEO 嘴里的故事。账单照样在，只是从工资栏挪到了 API 栏。"

#### 4.5 quotes（2-3 条，真实材料）
**来源严格**（不假冒第三人）：
- ✓ 原推作者自己说的（attr: "— @handle · 原推"）
- ✓ 报道原文摘录（attr: "— xx 报道原文"）
- ✓ X 评论区 top_replies 真有人说的（attr: "— @replier · 评论区"）
- ❌ 编造 / 假装某人说

**3 条标配**：主评 + 反驳 + 真实情景 / 数据细节。
**2 条**：当原文 + replies 真材料只够 2 条时（v3.10 排版优先级规则下也可能砍到 2）。

每条 `text`（英文/中文都行）+ optional `zh`（如果 text 是英文，加中译）+ `attr`。

#### 4.6 action（25-40 字，「本周尝试」actionable）
特征：
- **可量化 / 可执行** — 这周内能动手做完
- **不空泛** — "好好学习"❌，"本周写 1 篇 800 字公开内容"✓
- **PM 视角延伸** — 不是单纯学习建议，是「这个事件给你的 next step」

例：
- "本周写 1 篇 800 字公开内容（小红书/知乎/blog 任选），让现实验证你一次。"
- "下次 CEO 说「下一代会怎样」，记一笔——半年后看赌赢还是赌输。"
- "下载国家反诈中心 App，跑一次 AI 鉴定备用。"

### Step 5 — 排版优先级 check（v3.10 硬规则）

**优先级**：action > take > footer > quotes > story

实际操作：
1. story 字数控在 350-380（不超 380）
2. 如果某件 quotes 3 条 + story 380 字渲染溢出 → 砍 quote 到 2 条
3. 仍溢出 → 砍 story 50 字 / 1 段
4. **永远不能砍 action / take / footer / 4 个 section labels**

写完 8 件后用 Python check：
```python
import re
def strip_em(s): return re.sub(r"</?em>", "", s)
for e in events:
    chars = sum(len(strip_em(p)) for p in e["story_paragraphs"])
    assert chars <= 380, f"{e['id']} too long: {chars}"
    assert 2 <= len(e["quotes"]) <= 3
    assert 25 <= len(e["take"]) <= 50
    assert 25 <= len(e["action"]) <= 50
```

### Step 6 — 落盘 + Schema 验证（**到此为止**）

```bash
# 写出 final.json 到 daily/$DATE/digest/work/final.json （JSON 文件）
# 然后 Schema 验证：
python3 -c "from schemas.enriched import Daily; import json; Daily.model_validate(json.load(open('daily/$DATE/digest/work/final.json')))"
```

**验证通过即任务完成。立即退出，不要做任何额外的事。**

⚠ **绝对不要**在本 skill 内跑以下命令（它们由外层 `lines/digest/run.py` 接管）：
- ❌ `python3 lines/digest/render_html.py ...`
- ❌ `python3 lines/digest/screenshot.py ...`（启动 chrome subprocess 在 detached 环境会 hang）
- ❌ `python3 lines/digest/auto_post_md.py ...`
- ❌ `python3 lines/digest/auto_readme.py ...`
- ❌ 任何 `python3 -m http.server`、`./lines/digest/dev.sh` 之类的长驻进程

**Why 这样切分**：cron 触发时 `claude -p` 是无 TTY 的 detached 进程，启动 chrome headless 子进程会因 stdin/stdout pipe 不释放而 hang。把渲染/截图留给 run.py 的纯 Python 步骤跑，claude 写完 final.json 立即退出。

---

## DoD（达成定义，不达标不能交给 run.py）

本 skill 只负责到 final.json 验证。9 PNG / publish/post.md / README 由外层 run.py 接管。

- [ ] `final.json` Pydantic schema 验证通过
- [ ] 8 件齐
- [ ] 每件 story 字数 350-380（去 `<em>` 标签）
- [ ] 每件 story 3 段
- [ ] 每件 5-6 处 `<em>` 高光
- [ ] 每件 quotes 2-3 条（真材料，attr 标清来源）
- [ ] 每件 take 25-40 字（PM 狠话）
- [ ] 每件 action 25-40 字（actionable）
- [ ] 在职合规 grep（公司名 / 内部数据）= 0 hit

---

## 报告格式（一句话即可，然后立即退出）

```
✓ final.json written + schema OK. 8 events, X total story chars, Y total quotes.
```

**不要**列发布步骤、不要等待用户、不要启动任何长驻进程。run.py 会接管渲染。

---

## 常见 edge case

| 问题 | 处理 |
|---|---|
| enriched_raw 不到 30 条 | 选项可能不够 8 件 → 跑 fetch_aihot 拉更多 / 或接受 6-7 件本期 |
| 某事件 quotes 候选只 1 条 | 加「相关背景」/「原推延伸引语」补到 2 条最少 |
| action 框被 footer 重叠 | 立即砍该 event quotes 到 2 条 + 重渲染 |
| Pydantic 验证失败 | 看错误字段，最常见：忘填 source.platform 或 quotes 数组 |
| chrome 渲染字号 fallback（thin font）| screenshot.py 已加 `--virtual-time-budget=15000`，等 15s |

---

## 不可妥协的红线（重复，因为太重要）

1. **在职合规**：公司名 / 内部数据 / 工具 / 决策 — 一律不发
2. **真实性**：quotes 不假冒第三人，take 不编造数据
3. **DoD 不过不交付**：宁可少 1 件、宁可砍字数，也不发不达标的
4. **action > take > quotes > story** 优先级 — action 被截立即砍 quote

---

## 引用资源

- Schema：`lines/digest/schemas/enriched.py`
- 渲染：`lines/digest/render_html.py` + `lines/digest/templates/daily.html.j2`
- 截图：`lines/digest/screenshot.py`
- Design context：`.impeccable.md` + `archive/2026-05-12-self-media-ai-positioning-design.md`
- 项目宪法：`CLAUDE.md`

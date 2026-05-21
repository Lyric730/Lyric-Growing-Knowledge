# 日报人工审核 Checklist · 10-15 min

> 每次 `/daily YYYY-MM-DD` 跑完 + `lines/digest/run.py` 出完 9 PNG 之后，小刀老师按这份过。
> 通过 = 可发；任何一项不过 → 回去改 `final.json` 重 render。

---

## 1️⃣ 内容质量（5 min）

打开 `daily/<date>/digest/publish/daily.html` 浏览器看一遍。

### 标题 / 8 件选择
- [ ] 8 件齐（封面 + 8 张事件卡 = 9 slides）
- [ ] 每件标题钩子够强（你愿意为它点进去）
- [ ] 人名都带身份（如「谷歌前 CEO 施密特」「菲尔兹奖得主陶哲轩」）
- [ ] 比例符合 40/30/20/10（① 职场转型 / ② 反 AI 文盲 / ③ 工具拆解 / ④ 趣味）

### 正文
- [ ] 每件 3 段 story（不是 1 段冗长 / 不是 5 段碎片）
- [ ] 每件 5-6 处绿色 em 高光（合理：数字 / 锋利判断 / 关键概念）
- [ ] 每段首行缩进 2em（中文报道惯例）
- [ ] 共鸣点清晰（第 3 段「对你/我意味着什么」必有）

### Quotes（→ 评论区）
- [ ] 每件 2-3 条 quote
- [ ] attr 标清来源（"— @handle · 原推" / "— xx 报道原文" / "— @replier · 评论区"）
- [ ] **不假冒第三人**（grep 一下：没有 attr 是空的或编造名字）

### Take（→ 小刀说）
- [ ] 每件 1 句 25-40 字
- [ ] PM 视角狠话（带反差 / 第一视角 / 不说理）
- [ ] 没编造数据

### Action（→ 本周尝试）
- [ ] 每件 1 句 25-40 字
- [ ] Actionable（这周内能动手做完）
- [ ] **不空泛**（"好好学习"❌ / "本周写 1 篇 800 字"✓）

---

## 2️⃣ 排版 / 视觉抽查（3 min）

打开 PNG 看 3 张关键：

| PNG | 检查项 |
|---|---|
| `01-cover.png` | 8 件等权列表 / 副标可读 / meta 白色不灰 |
| `02-event-01.png` | rail+title+meta+story+quotes+take+action+footer 完整不溢出 |
| `09-event-08.png` | action 没被 footer 重叠 / footer 完整可见 |

- [ ] 9 张 PNG 严格 1080×1440（PIL 命令验证：`python3 -c "from PIL import Image; [print(Image.open(f'daily/<date>/digest/publish/images/{f}').size) for f in sorted(...)]"`）
- [ ] 没看到 grain 背景小点点
- [ ] 背景近白（chroma 0.005）不是米黄
- [ ] 4 个 section labels 都明显（→ 报道 / 评论区 / 小刀说 / 本周尝试）

---

## 3️⃣ 在职合规 grep（1 min）

```bash
grep -i "字节\|腾讯\|阿里\|内部 PRD\|本周 OKR\|@team" daily/<date>/digest/publish/post.md daily/<date>/digest/work/final.json
```

- [ ] grep 0 hit（auto_post_md.py 已自动 grep，但手工改正文后必须再跑）

---

## 4️⃣ Post.md（2 min）

打开 `daily/<date>/digest/publish/post.md`：

- [ ] 4 个标题候选里选 1 个（首选 / 备选 / 自己改）
- [ ] 正文 200-400 字（不超 1000）
- [ ] 标签 12-15 个（流量入口 + 精准受众 + 长尾混搭）
- [ ] 「哪一条「本周尝试」你打算真做？」结尾钩子是否换更带感

---

## 5️⃣ 发布前最后 3 步

- [ ] 9 张 PNG 复制到 Windows 桌面（`\\wsl.localhost\Ubuntu\home\lyric\Making money\Lyric-Self-Improve\projects\Self-Media\daily\<date>\publish\images\`）
- [ ] 小红书 App：按 `01 → 02 → ... → 09` **顺序**上传（顺序乱了视觉链断）
- [ ] 发布时间：晚间 19-22 点（小红书流量峰）

---

## 🔴 触发回滚的红线（任一发生 → 不能发）

- ❌ action 框被 footer 重叠或被截
- ❌ footer 文字不可见（cream 上 ink-soft 13px 是底线）
- ❌ PNG 不是 1080×1440
- ❌ 出现公司名 / 内部数据
- ❌ quotes 编造（attr 看着假）
- ❌ 任何一件 story < 300 字（密度不够 = 不达标 5/12 baseline）

→ 回 `final.json` 改 → 跑 `python3 lines/digest/run.py <date> --only-render`（跳过 fetch + enrich）

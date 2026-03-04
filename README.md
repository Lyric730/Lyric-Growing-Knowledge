# Lyric Growing Knowledge

一个用于 **AI 增长工作流** 的协作仓库：
- 你（Lyric）负责方向与审核
- 刀哥负责产出草案、结构化沉淀、提交 PR

## 仓库目标
把增长工作做成可复用系统，而不只是一次次临时动作。

## 目录结构
- `content/`：选题池、内容草稿、发布计划
- `assets/`：素材索引（不建议放大文件本体）
- `reports/`：周报、复盘、实验记录
- `prompts/`：高频提示词、工作流提示模板
- `POLICY/`：协作规则、审核标准、风险边界

## 协作流程（核心）
1. 提需求（目标、受众、约束、截止时间）
2. 刀哥开分支：`feat/...` `fix/...` `docs/...`
3. 刀哥提交改动并发起 PR
4. Lyric 审核（内容质量 / 风险 / 可执行性）
5. 通过后 merge 到 `main`

## 分支命名
- `feat/<topic>`：新增能力或内容模块
- `docs/<topic>`：文档规范/模板更新
- `fix/<topic>`：修正错误

例如：
- `feat/x-matrix-weekly-plan`
- `docs/pr-review-checklist`

## 建议保护规则
- `main` 禁止直接 push
- 必须通过 PR 合并
- 至少 1 个 reviewer（你自己）

## 快速开始
先看：
- `CONTRIBUTING.md`
- `.github/pull_request_template.md`
- `POLICY/review-checklist.md`

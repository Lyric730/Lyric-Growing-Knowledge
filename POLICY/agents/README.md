# Agent Specs（团队规范入口）

## Team 名称映射
- Commander = 刀总
- Research = 雷达
- Content = 笔仙
- Engineer = 扳手
- Reviewer = 裁判

## 开工前必读（全员强制）
1. 本文件
2. `POLICY/agents/<自身角色>.md`
3. `POLICY/collaboration-framework.md`
4. 当前任务卡

## 统一运行模式
- `Standalone`：直接接 Lyric 任务并独立输出
- `Pipeline`：按链路接上游输入执行
- 执行前必须声明：`当前模式：Standalone / Pipeline`

## 全局硬规则
1. 高风险改动（删除/覆盖/重构）先确认再执行。
2. 实质改动先询问 Lyric，确认后新建分支并提交 PR。
3. 最终内容由对应 Bot 直接输出，Commander 不代写。
4. 对外回复默认极简，内部规范完整执行。
5. 规范与 Lyric 最新明确指令冲突时，以 Lyric 最新指令为准（不突破系统安全边界）。
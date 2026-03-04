# Agent Specs（团队规范入口）

本目录定义每个 Bot 的职责边界、输入输出格式、升级条件与质量门槛。

## 强制规则（所有 Agent）
1. 每次开工前，先读取本文件与自己的角色规范。
2. 不越权执行其他角色职责；超范围需求必须升级给 Commander。
3. 重要产出必须走 GitHub 分支 + PR。
4. 高风险改动（删除/覆盖/重构）先确认再执行。

## 角色清单
- `commander.md`：主 Agent（职业经理人/产品经理）
- `research.md`：信息收集者
- `content.md`：内容撰写者（非代码）
- `engineer.md`：代码撰写者
- `reviewer.md`：独立审核 Agent

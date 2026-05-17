# huoshanbei — 思源学长

首届"火山杯"AI 应用创新大赛参赛项目。

- **作品名**：思源学长（siyuan-senior）
- **方向**：01 服务一校多区建设
- **平台**：扣子（Coze） + 豆包 1.6 Pro
- **参赛者**：刘又瑄（北京交通大学威海校区，solo）
- **状态**：🟢 spike（设计阶段，未开发）

## 时间线（绝对日期）

| 阶段 | 时间 | 当前进度 |
|------|------|---------|
| 报名 + 创意提交 | 2026-05-15 ~ 05-25 | 进行中 |
| 创意审核 + Coze 资源发放 | 2026-05-26 ~ 05-31 | 等待 |
| 开发 + 作品提交 | 2026-06-01 ~ 06-21 | 未开始 |
| 评审 + 颁奖 | 2026-06 下旬 | 未开始 |

## 项目结构

```
huoshanbei/
├── README.md             # 本文件
├── docs/
│   └── design.md         # 完整设计 spec（Section 1-3）
├── knowledge/            # 知识库源材料（四分区）
│   ├── common/           # 三校区通用
│   ├── haidian/          # 海淀本部
│   ├── weihai/           # 威海校区
│   └── xiongan/          # 雄安校区
├── prompts/              # Persona prompt / 子流程 prompt
├── workflows/            # Coze 工作流逻辑设计
└── tests/                # 测试用例（50 标准题 + 真用户）
```

## 下一步

1. Section 3 (技术栈/Coze 实现/测试策略) 待 review 与 approve
2. 知识库 4 分区材料收集（5/17–5/25）
3. 等 5/26 拿到 Coze 子账号 → 把设计搬到平台

## 相关文档

- 完整设计：[`docs/design.md`](docs/design.md)
- 公众号原文（赛事详情）：https://mp.weixin.qq.com/s/ug2fTs6QfaCBvzON2-LNNw

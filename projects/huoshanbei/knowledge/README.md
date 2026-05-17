# Knowledge Base 源材料

供 Coze 4 个独立 KB 导入的源材料。**分区即 KB**——目录名对应 Coze 平台里 KB 名。

## 分区

| 目录 | KB 名 | 范围 |
|------|-------|------|
| `common/` | siyuan-common | 三校区通用：校史 / 校规 / 学籍管理 / SSO / 全校性活动 |
| `haidian/` | siyuan-haidian | 北京海淀本部专属 |
| `weihai/` | siyuan-weihai | 威海校区专属 |
| `xiongan/` | siyuan-xiongan | 雄安校区专属 |

## 每个分区内子目录（对齐结构便于 M4 跨校区对比）

```
<campus>/
├── 入学/        # 录取、报到、住宿、医保、银行卡、迎新流程
├── 校园生活/    # 宿舍、食堂、图书馆、运动设施、班车
├── 教务服务/    # 选课注册、成绩、转专业、辅修（信息向，不操作）
├── 行政服务/    # 学生证、户籍、奖助贷、保险报销、出入校
└── 周边/        # 地理位置、交通、商圈、医院
```

## 文档命名规范

`<主题>__<信息源>__<采集日期>.md`

例：`迎新报到流程__威海校区学生处官网__2026-05-17.md`

**强制元数据头**（每个 .md 文档开头）：

```markdown
---
title: 迎新报到流程
campus: weihai
category: 入学
source: 威海校区学生处官网
source_url: https://wh.bjtu.edu.cn/...
collected_at: 2026-05-17
last_verified: 2026-05-17
---
```

> `source` + `source_url` 是 RAG 回答时引用所必需，**不能省**。

## 当前状态

🟢 spike — 仅目录结构占位，待 5/17 起开始填充

# 🤖 Kael PM — Jira Skill 蒸馏版

> **IcestoneTech Scrum 工作流完整指南**  
> 基于实战经验蒸馏，涵盖 Jira REST API v3 + Agile API 全操作手册

---

## 📋 项目信息

| 字段 | 值 |
|------|-----|
| **Jira 站点** | `https://icestonetech.atlassian.net` |
| **项目** | LFX (LimFx, Company-Managed Classic Scrum) |
| **项目 ID** | 10067 |
| **Board ID** | 35 |
| **Sprint 1 ID** | 103 (2026-04-14 ~ 04-28) |

---

## 📁 文件结构

```
jira-skill-distilled/
├── README.md              # 本文件 — 快速导航
├── core/
│   ├── auth.py            # 认证 & 基础 API 客户端
│   ├── issue_ops.py       # Issue CRUD 操作
│   ├── sprint_ops.py      # Sprint 管理
│   ├── link_ops.py        # Issue 关联 (Polaris, Blocks, Relates)
│   └── attachment_ops.py  # 文件附件上传
├── workflows/
│   ├── sprint_planning.md # Sprint 规划 SOP
│   ├── bug_triage.md      # Bug 分类工作流
│   └── scrum_sop.md       # 完整 Scrum Master SOP
├── reference/
│   ├── issue_types.md     # Issue 类型 & ID 速查
│   ├── issue_map.md       # LFX Sprint 1 全量 Issue 映射表
│   ├── link_rules.md      # 关联规则图谱
│   └── pitfalls.md        # 已知坑 & 解决方案
└── templates/
    ├── adf_builder.py     # ADF (Atlassian Document Format) 构造器
    └── epic_template.py   # Epic/Story/Feature 描述模板
```

---

## 🚀 快速开始

```python
# 1. 配置认证
import os
TOKEN = open(os.path.expanduser("~/.hermes/secrets/jira_token")).read().strip()

# 2. 导入客户端
from core.auth import jira_request, agile_request

# 3. 搜索 Issues
result, _ = jira_request("POST", "/search/jql", {
    "jql": "project = LFX AND sprint = 103",
    "maxResults": 50,
    "fields": ["summary", "status", "issuetype"]
})
```

---

## ⚠️ 铁律 (PM 工作流)

1. **所有 PM 操作直接通过 Jira API** — 禁止在本地创建 Scrum 文件
2. **三层结构**：Epic → Story → Feature/Task（缺一不可）
3. **文档附件**直接上传到对应 Jira issue（PRD→Epic, 设计→Feature）
4. **Issue 创建后立即加入 Sprint**（不自动归入）
5. **Story↔Feature 关联**用 `Polaris work item link`（不能用 parent 字段）

---

## 📊 Issue 层级约束

```
Epic (level 1)
  └─[parent]──► Story (level 0)
        └─[Polaris work item link]──► Feature/Task (level 0)
              └─[parent]──► Sub-task (level -1)
```

> **关键**：Story 和 Feature 同为 level 0，无法用 `parent` 字段关联，必须用 issueLink。

---

*维护者：Kael (IcestoneTech AI PM) | 最后更新：2026-04-17*

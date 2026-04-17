# 🤖 Jira Skill 蒸馏版

> **Scrum 工作流完整指南**  
> 基于实战经验蒸馏，涵盖 Jira REST API v3 + Agile API 全操作手册
> 适用于 Classic Company-Managed Scrum 项目

---

## 📋 快速配置

创建 `jira-config.json`（参考 `examples/jira-config.example.json`）：

```json
{
  "jira_base": "https://your-org.atlassian.net",
  "email": "you@your-org.com",
  "project_key": "PROJ",
  "board_id": 1,
  "issue_types": {
    "Epic": "10000",
    "Story": "10008",
    "Feature": "10050",
    "Task": "10054",
    "Sub-task": "10055",
    "Bug": "10051",
    "Fix": "10052",
    "Improvement": "10053"
  }
}
```

或使用环境变量：`JIRA_BASE`、`JIRA_EMAIL`、`JIRA_PROJECT_KEY`、`JIRA_BOARD_ID`、`JIRA_TOKEN`

> ⚠️ Issue Type ID 因项目不同，用 `GET /rest/api/3/issuetype` 查询你的项目的 ID

---

## 📁 文件结构

```
jira-skill-distilled/
├── SKILL.md               # AgentSkill 入口
├── README.md              # 本文件 — 快速导航
├── jira-config.json       # 项目配置（需自行创建，已 gitignore）
├── core/
│   ├── config.py          # 集中配置（env var + config file）
│   ├── auth.py            # 认证 & 基础 API 客户端
│   ├── issue_ops.py       # Issue CRUD 操作
│   ├── sprint_ops.py      # Sprint 管理 & 查询
│   ├── dev_ops.py         # 研发日常操作（领任务/工时/评论/JQL shortcuts）
│   ├── link_ops.py        # Issue 关联 (Polaris, Blocks, Relates)
│   └── attachment_ops.py  # 文件附件上传
├── workflows/
│   └── scrum_sop.md       # 完整 Scrum Master SOP
├── reference/
│   ├── issue_types.md     # Issue 类型 & 层级速查
│   └── pitfalls.md        # 已知坑 & 解决方案
├── templates/
│   └── adf_builder.py     # ADF (Atlassian Document Format) 构造器
└── examples/
    ├── jira-config.example.json  # 配置文件模板
    └── issue_map_lfx.md          # LFX 项目 Issue 映射示例
```

---

## 🚀 快速开始

```python
from core import *

# 查看我今天的任务
tasks = todo_today()

# 领任务
assign_to_me("PROJ-6")

# 状态流转（支持模糊匹配）
smart_transition("PROJ-6", "doing")   # → In Progress

# 记工时
add_worklog("PROJ-6", "2h", comment="完成 API 开发")

# 创建 Issue
from templates.adf_builder import feature_description
desc = feature_description("实现登录", "POST /auth/login", ["用户服务"], ["✅ 返回 JWT"])
key = create_feature("实现登录接口", desc, epic_key="PROJ-1")
add_to_sprint([key])  # 自动加入 active sprint
```

---

## ⚠️ 铁律

1. **描述字段必须用 ADF 格式**（用 `templates/adf_builder.py`）
2. **三层结构**：Epic → Story → Feature/Task（缺一不可）
3. **Issue 创建后立即加入 Sprint**（不自动归入）
4. **Story↔Feature 关联**用 `Polaris work item link`（不能用 parent 字段）
5. **Sprint 操作用 Agile API**（`agile_request`），不是 REST API v3
6. **批量操作加 `time.sleep(0.3)` 防限流**

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

*原作者：Kael | 通用化 & 研发扩展：Forge*

# SKILL.md — Jira Skill (Distilled)

> Scrum 工作流操作手册 — Jira REST API v3 + Agile API
> 适用于任何 Classic Company-Managed Scrum 项目

## When to Use

- 用户提到 Jira、Sprint、Issue、看板、领任务、工时
- 需要查询/创建/更新 Jira Issue
- Sprint 规划、状态流转、任务分配

## Setup

创建 `jira-config.json`（参考 `examples/jira-config.example.json`）或设置环境变量：
- `JIRA_BASE` — Jira 站点 URL
- `JIRA_EMAIL` — 认证邮箱
- `JIRA_TOKEN` — API Token
- `JIRA_PROJECT_KEY` — 项目 Key
- `JIRA_BOARD_ID` — Board ID

Issue Type ID 因项目不同，用 `GET /rest/api/3/issuetype` 查询后配置到 `jira-config.json`。

## Quick Reference

### 核心模块
| 模块 | 用途 |
|------|------|
| `core/config.py` | 集中配置（env var + config file，零硬编码） |
| `core/auth.py` | 认证 & API 客户端 |
| `core/issue_ops.py` | Issue CRUD |
| `core/sprint_ops.py` | Sprint 查询 & 管理 |
| `core/dev_ops.py` | 研发日常（领任务/工时/评论/JQL shortcuts） |
| `core/link_ops.py` | Issue 关联 |
| `core/attachment_ops.py` | 文件附件上传 |
| `templates/adf_builder.py` | ADF 文档格式构造器 |

### 研发常用操作

```python
from core import *

# 我今天要做什么
tasks = todo_today()

# 领任务
assign_to_me("PROJ-6")

# 状态流转（支持模糊匹配）
smart_transition("PROJ-6", "doing")  # → In Progress

# 记工时
add_worklog("PROJ-6", "2h", comment="完成 API 端点开发")

# 看未分配任务
unassigned = unassigned_tasks()

# 看评论
comments = get_comments("PROJ-6")
```

### 铁律
1. 描述字段必须用 ADF 格式（用 `templates/adf_builder.py`）
2. Sprint 操作用 Agile API（`agile_request`），不是 REST API v3
3. Story ↔ Feature 用 Polaris link，不能用 parent 字段
4. Issue 创建后必须手动加入 Sprint
5. 批量操作加 `time.sleep(0.3)` 防限流

### 参考文档
- `reference/issue_types.md` — Issue 类型 & 层级速查
- `reference/pitfalls.md` — 已知坑 & 解决方案
- `workflows/scrum_sop.md` — Scrum Master SOP
- `examples/` — 配置模板 & 示例数据

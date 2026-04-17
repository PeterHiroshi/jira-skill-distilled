# SKILL.md — Jira Skill (Distilled)

> IcestoneTech Scrum 工作流 — Jira REST API v3 + Agile API 操作手册
> 蒸馏自 Kael (PM/PD)，Forge 扩展研发操作

## When to Use

- 用户提到 Jira、Sprint、Issue、看板、领任务、工时
- 需要查询/创建/更新 Jira Issue
- Sprint 规划、状态流转、任务分配

## Quick Reference

### 项目配置
- Jira Site: `https://icestonetech.atlassian.net`
- Project: LFX (Company-Managed Classic Scrum)
- 配置集中在 `core/config.py`，支持环境变量覆盖

### 核心模块
| 模块 | 用途 |
|------|------|
| `core/auth.py` | 认证 & API 客户端 |
| `core/config.py` | 集中配置（env var 覆盖） |
| `core/issue_ops.py` | Issue CRUD |
| `core/sprint_ops.py` | Sprint 查询 & 管理 |
| `core/dev_ops.py` | 研发日常操作（领任务/工时/评论/JQL shortcuts） |
| `core/link_ops.py` | Issue 关联 |
| `core/attachment_ops.py` | 文件附件上传 |
| `templates/adf_builder.py` | ADF 文档格式构造器 |

### 研发常用操作

```python
from core import *

# 我今天要做什么
tasks = todo_today()

# 领任务
assign_to_me("LFX-6")

# 状态流转（支持模糊匹配）
smart_transition("LFX-6", "doing")  # → In Progress
smart_transition("LFX-6", "done")   # → Done

# 记工时
add_worklog("LFX-6", "2h", comment="完成 API 端点开发")

# 看未分配任务
unassigned = unassigned_tasks()

# 看评论
comments = get_comments("LFX-6")
```

### 铁律
1. 描述字段必须用 ADF 格式（用 `templates/adf_builder.py`）
2. Sprint 操作用 Agile API（`agile_request`），不是 REST API v3
3. Story ↔ Feature 用 Polaris link，不能用 parent 字段
4. Issue 创建后必须手动加入 Sprint
5. 批量操作加 `time.sleep(0.3)` 防限流

### 参考文档
- `reference/issue_types.md` — Issue 类型 & ID 速查
- `reference/issue_map.md` — LFX Sprint 1 全量映射
- `reference/pitfalls.md` — 已知坑 & 解决方案
- `workflows/scrum_sop.md` — Scrum Master SOP

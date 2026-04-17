# Issue 类型 & 层级速查

> Classic Company-Managed Scrum 项目通用参考
> 具体 Issue Type ID 因项目不同，配置在 `jira-config.json` 的 `issue_types` 字段

## 常见 Issue Types

| 名称 | 用途 | 层级 |
|------|------|------|
| Epic | 战略主题/里程碑，对应 User Story 集合 | L1 |
| Story | 用户视角需求，含 AC，挂在 Epic 下 | L0 |
| Feature | 新功能实现，对应 Story 的代码交付 | L0 |
| Improvement | 体验优化/性能重构 | L0 |
| Bug | 缺陷报告，关联到发现的 Feature/Story | L0 |
| Fix | Bug 修复任务，被 Bug 阻塞 | L0 |
| Task | 通用工程任务（测试/文档/部署） | L0 |
| Sub-task | 挂在 Task/Story 下的拆分工作项 | L-1 |

## 层级关系

```
Epic (level 1)           — 战略主题层
  └─ Story (level 0)     — 用户故事层（通过 parent 字段挂在 Epic 下）
  └─ Feature (level 0)   — 实现任务层（通过 Polaris link 关联 Story）
  └─ Task (level 0)      — 工程任务层
  └─ Bug (level 0)       — 缺陷层
       └─ Sub-task (level -1)  — 子任务（通过 parent 字段）
```

## 关键约束

- **Epic → Story**：用 `parent` 字段 ✅（层级差为 1，合法）
- **Story ↔ Feature**：用 `Polaris work item link` ✅（同为 level 0，parent 会报错 ❌）
- **Task → Sub-task**：用 `parent` 字段 ✅

## 优先级

| 名称 | 用途 |
|------|------|
| Highest | P0 关键路径 |
| High | Sprint 核心功能 |
| Medium | 正常优先级 |
| Low | 可延期 |
| Lowest | Backlog |

## 推荐 Label 体系

| Label | 含义 |
|-------|------|
| `backend` | 后端工程师负责 |
| `frontend` | 前端工程师负责 |
| `qa` | QA 负责 |
| `pm` | PM 负责 |
| `fullstack` | 跨角色协作 |
| `sp-N` | Story Points 值 |

> ⚠️ Issue Type ID 因 Jira 实例和项目不同而不同。
> 使用 `GET /rest/api/3/issuetype` 获取你的项目的 ID，然后配置到 `jira-config.json`。

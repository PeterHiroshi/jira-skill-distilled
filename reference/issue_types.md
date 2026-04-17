# Issue 类型 & ID 速查

> LFX (Company-Managed Classic Scrum) Issue Types

## Issue Type 表

| 名称 | ID | 图标 | 层级 | 用途 |
|------|----|------|------|------|
| Epic | 10000 | 🟣 紫色闪电 | L1 | 战略主题/里程碑，对应 User Story 集合 |
| Story | 10008 | 📖 绿色书签 | L0 | 用户视角需求，含 AC，挂在 Epic 下 |
| Feature | 10050 | 💡 金色灯泡 | L0 | 新功能实现，对应 Story 的代码交付 |
| Improvement | 10053 | ✨ 橙色圆圈 | L0 | 体验优化/性能重构 |
| Bug | 10051 | 🐛 红色虫子 | L0 | 缺陷报告，关联到发现的 Feature/Story |
| Fix | 10052 | 🔧 蓝色斜线 | L0 | Bug 修复任务，被 Bug 阻塞 |
| Task | 10054 | ✅ 蓝色对勾 | L0 | 通用工程任务（测试/文档/部署） |
| Sub-task | 10055 | 🔹 蓝色子图标 | L-1 | 挂在 Task/Story 下的拆分工作项 |

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

| 名称 | 颜色 | 用途 |
|------|------|------|
| Highest | 🔴 红色 | P0 关键路径 |
| High | 🟠 橙色 | Sprint 核心功能 |
| Medium | 🟡 黄色 | 正常优先级 |
| Low | 🔵 蓝色 | 可延期 |
| Lowest | ⚫ 灰色 | Backlog |

## Label 体系

| Label | 含义 | 适合过滤 |
|-------|------|---------|
| `backend` | 后端工程师负责 | 分配给 BE |
| `frontend` | 前端工程师负责 | 分配给 FE |
| `qa` | QA 负责 | 分配给 QA |
| `pm` | PM 负责 | 分配给 PM |
| `fullstack` | 跨角色协作 | 全员 |
| `feature` | 功能类工作项 | Sprint Planning |
| `improvement` | 优化类工作项 | Sprint Planning |
| `fix` | 修复类工作项 | Bug Triage |
| `US-001`~`US-005` | 归属 User Story | Epic 过滤 |
| `sp-N` | Story Points 值 | Velocity 计算 |

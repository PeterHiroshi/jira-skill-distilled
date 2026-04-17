# Scrum Master SOP — 完整工作流

> 通用 Scrum Master 操作规程（基于 Jira REST API v3 + Agile API）

---

## Sprint Planning

### 步骤
1. 从 Backlog 选取 P0/P1 Feature，估算 Story Points（用 `sp-N` label）
2. 建立三层结构：**Epic → Story → Feature/Task**（顺序不能错）
3. 为每个 Issue 分配角色 label（`backend`/`frontend`/`qa`）
4. 将所有 Issue 加入 Sprint：`add_to_sprint(["PROJ-25", "PROJ-26"])`
5. 确认 Improvement 挂在对应 Feature 下（不单独排期）

### Issue 创建顺序
```
1. 创建 Epic（战略主题）
2. 创建 Story（用户故事，设 parent=Epic Key）
3. 创建 Feature/Task（设 customfield_10014=Epic Key）
4. 用 Polaris link 关联 Feature → Story
5. 批量加入 Sprint
```

---

## Daily Standup

### 查看阻塞
```python
blocked_issues = search_issues(
    f"project = {CFG.project_key} AND issueLinksType = 'is blocked by' AND status != Done AND sprint in openSprints()"
)
```

### 按角色过滤
```python
be_tasks = search_issues(
    f"project = {CFG.project_key} AND labels = backend AND sprint in openSprints() AND status = 'In Progress'"
)
```

---

## Bug Triage

```
1. 创建 Bug issue（issuetype=Bug）
   └─ 关联到发现它的 Feature：link_relates(bug_key, feature_key)
   
2. 创建 Fix issue（issuetype=Fix）
   └─ 设置 Epic Link 同上游 Epic：set_epic_link(fix_key, epic_key)
   └─ 设置阻塞：link_blocks(bug_key, fix_key)  # Bug 阻塞 Fix

3. Fix 合并后：smart_transition(bug_key, "done")
```

---

## Sprint Review

```python
done_features = search_issues(
    f"project = {CFG.project_key} AND issuetype = Feature AND status = Done AND sprint in openSprints()"
)

open_bugs = search_issues(
    f"project = {CFG.project_key} AND issuetype = Bug AND status != Done AND sprint in openSprints()"
)
```

---

## Retrospective 质量指标

```python
all_issues = search_issues(
    f"project = {CFG.project_key} AND sprint in openSprints()", max_results=100
)

features = [i for i in all_issues if i["fields"]["issuetype"]["name"] == "Feature"]
bugs = [i for i in all_issues if i["fields"]["issuetype"]["name"] == "Bug"]

quality_ratio = len(bugs) / len(features) if features else 0
print(f"质量比率: {len(bugs)} bugs / {len(features)} features = {quality_ratio:.1%}")
```

---

## 文档发布规范

| 文档类型 | 上传到 | 示例 |
|----------|--------|------|
| PRD | 对应 Epic | `upload_attachment("PROJ-1", "docs/prd.pdf")` |
| 设计稿/原型 | 对应 Feature | `upload_attachment("PROJ-6", "docs/design.pdf")` |
| 测试报告 | 对应 Task | `upload_attachment("PROJ-10", "docs/test-report.pdf")` |

> ⚠️ 禁止在本地 workspace 创建 Scrum 文件（Sprint Plan、Kanban、User Stories 等）
> ⚠️ 所有 PM 操作直接通过 Jira API 执行

---

*基于 Kael 的 Scrum Master SOP，通用化改造 by Forge*

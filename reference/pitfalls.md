# ⚠️ 已知坑 & 解决方案

> 来自实战经验，避免踩重复的坑。

---

## 1. Story → Feature parent 报错

**坑**：在 Classic Company-Managed 项目中，Feature 和 Story 同为 `hierarchyLevel: 0`，用 `parent` 字段关联会报：
```
"Given parent work item does not belong to appropriate hierarchy."
```

**解**：用 `Polaris work item link` issueLink 替代。⚠️ 方向经实测校正：本站点
`inwardIssue` 读作 "implements"，`outwardIssue` 读作 "is implemented by"，所以
**Feature 必须是 inwardIssue**（旧文档写反，会导致 Story 显示 "implements → Feature"）：
```python
jira_request("POST", "/issueLink", {
    "type": {"name": "Polaris work item link"},
    "inwardIssue":  {"key": feature_key},  # Feature: "implements"
    "outwardIssue": {"key": story_key},    # Story:   "is implemented by"
})
```

---

## 2. 文件上传 403 XSRF Error

**坑**：上传附件时缺少 `X-Atlassian-Token: no-check` header，返回 403。

**解**：必须带此 header：
```python
headers={
    "Authorization": f"Basic {auth}",
    "X-Atlassian-Token": "no-check",  # ⚠️ 必须！
    "Content-Type": f"multipart/form-data; boundary={boundary}",
}
```

---

## 3. boundary 字符串含 `=` 导致解析失败

**坑**：multipart boundary 中含 `=` 字符（如 `boundary=abc`），部分服务器拒绝。

**解**：boundary 只用字母+数字+连字符：
```python
boundary = "----JiraFileBoundary7x9k"  # ✅
# boundary = "abc=def"  # ❌
```

---

## 4. 文件上传响应是数组

**坑**：上传附件的响应是 JSON **数组**，不是对象，直接取 `result["id"]` 会 KeyError。

**解**：
```python
result = json.loads(resp.read())
attachment = result[0]  # ✅ 数组第一个元素
```

---

## 5. Issue 创建后不自动归入 Sprint

**坑**：创建 Issue 后，`sprint` 字段默认为空，不会自动加入当前 active Sprint。

**解**：创建后立即调用 Agile API：
```python
agile_request("POST", f"/sprint/{SPRINT_ID}/issue", {
    "issues": ["LFX-25", "LFX-26"]
})
```

---

## 6. Sprint API 用错了路径

**坑**：Sprint 操作用 `/rest/api/3/sprint/...` 返回 404。

**解**：Sprint 必须用 Agile API：
```python
# ✅ 正确
f"{JIRA_BASE}/rest/agile/1.0/sprint/{sprint_id}/issue"

# ❌ 错误
f"{JIRA_BASE}/rest/api/3/sprint/{sprint_id}/issue"
```

---

## 7. 旧版 JQL 搜索 API 已废弃

**坑**：`GET /rest/api/3/search?jql=...` 已废弃（仍可用但不推荐）。

**解**：使用 POST 方式：
```python
jira_request("POST", "/search/jql", {
    "jql": "project = LFX AND sprint = 103",
    "maxResults": 50,
    "fields": ["summary", "status"]
})
```

---

## 8. 描述字段不能用纯文本

**坑**：`"description": "plain text"` 会被拒绝，返回 400 Bad Request。

**解**：必须用 ADF 格式：
```python
"description": {
    "type": "doc",
    "version": 1,
    "content": [{
        "type": "paragraph",
        "content": [{"type": "text", "text": "your text"}]
    }]
}
```

---

## 9. Next-gen 项目不支持 Epic Link

**坑**：Next-gen（Team-managed）项目中，`customfield_10014`（Epic Link）字段不可用。

**解**：
- 检测项目类型：`project.get("simplified") == True` 则是 next-gen
- Next-gen 中用 `"Relates"` issueLink 替代 Epic Link
- **推荐**：新项目选 Classic（Company-Managed）以获得完整 API 支持

---

## 10. Next-gen 项目无法通过 API 创建 Issue Type

**坑**：`POST /issuetype` with `scope.type=PROJECT` 在 next-gen 项目中不工作，scope 永远返回 null。

**解**：只能在 UI 操作：
`Project Settings → Issue types → Add issue type`

---

## 11. Token 路径配置

**坑**：不同 agent 的 token 存储位置不同，硬编码路径会找不到文件。

**解**：config.py 按优先级搜索多个路径，也支持 `JIRA_TOKEN` 环境变量。详见 `core/config.py`。

---

## 12. 批量操作需要 rate limiting

**坑**：连续请求过快会触发 Atlassian API 限流（429 Too Many Requests）。

**解**：批量操作时加 `time.sleep(0.3)` 间隔。

---

*基于 Kael 的实战整理，通用化改造 by Forge*

"""
core/dev_ops.py — 研发日常操作

覆盖研发工作流：领任务 → 更新进度 → 记工时 → 看评论
"""
from .auth import jira_request, agile_request
from .config import CFG
from .sprint_ops import get_active_sprint


# ──────────────────────────────────────
# Assignee
# ──────────────────────────────────────

def get_myself() -> dict:
    """获取当前认证用户信息（accountId, displayName, emailAddress）"""
    result, err = jira_request("GET", "/myself")
    if err:
        raise RuntimeError(f"get_myself failed: {err}")
    return result


def find_user(query: str) -> list:
    """
    按名字/邮箱搜索 Jira 用户，返回匹配列表

    Args:
        query: 搜索关键词（名字片段或邮箱）
    """
    result, err = jira_request("GET", f"/user/search?query={query}&maxResults=10")
    if err:
        raise RuntimeError(f"find_user failed: {err}")
    return result


def assign_issue(issue_key: str, account_id: str = None):
    """
    分配 Issue 给指定用户

    Args:
        account_id: Jira accountId。传 None = 取消分配。
                    传 "-1" = 自动分配（如果配置了规则）。
    """
    payload = {"accountId": account_id}
    result, err = jira_request("PUT", f"/issue/{issue_key}/assignee", payload)
    if err:
        raise RuntimeError(f"assign_issue failed: {err}")
    return result


def assign_to_me(issue_key: str):
    """把 Issue 分配给自己（快捷方式）"""
    me = get_myself()
    return assign_issue(issue_key, me["accountId"])


# ──────────────────────────────────────
# Worklog / Time Tracking
# ──────────────────────────────────────

def add_worklog(issue_key: str, time_spent: str, comment: str = None,
                started: str = None) -> dict:
    """
    记录工时

    Args:
        issue_key: e.g. "LFX-6"
        time_spent: Jira 时间格式，e.g. "2h", "1d", "30m", "1h 30m"
        comment: 工作内容描述（可选）
        started: 开始时间 ISO 8601，e.g. "2026-04-17T09:00:00.000+0800"
                 不传则使用当前时间
    """
    payload = {"timeSpent": time_spent}
    if started:
        payload["started"] = started
    if comment:
        payload["comment"] = {
            "type": "doc",
            "version": 1,
            "content": [{
                "type": "paragraph",
                "content": [{"type": "text", "text": comment}],
            }],
        }
    result, err = jira_request("POST", f"/issue/{issue_key}/worklog", payload)
    if err:
        raise RuntimeError(f"add_worklog failed: {err}")
    return result


def get_worklogs(issue_key: str) -> list:
    """获取 Issue 的所有工时记录"""
    result, err = jira_request("GET", f"/issue/{issue_key}/worklog")
    if err:
        raise RuntimeError(f"get_worklogs failed: {err}")
    return result.get("worklogs", [])


# ──────────────────────────────────────
# Comments (读取)
# ──────────────────────────────────────

def get_comments(issue_key: str, max_results: int = 50) -> list:
    """
    获取 Issue 的评论列表

    Returns:
        list of comment dicts, 每个含 author, body, created, updated
    """
    result, err = jira_request(
        "GET", f"/issue/{issue_key}/comment?maxResults={max_results}&orderBy=-created"
    )
    if err:
        raise RuntimeError(f"get_comments failed: {err}")
    return result.get("comments", [])


# ──────────────────────────────────────
# 研发常用 JQL Shortcuts
# ──────────────────────────────────────

def my_sprint_tasks(status: str = None, sprint_id: int = None) -> list:
    """
    获取「我在当前 Sprint 的任务」

    Args:
        status: 可选过滤，如 "To Do", "In Progress", "Done"
        sprint_id: 指定 Sprint ID，不传则自动获取 active sprint
    """
    from .issue_ops import search_issues

    if not sprint_id:
        active = get_active_sprint()
        if not active:
            raise RuntimeError("No active sprint found")
        sprint_id = active["id"]

    me = get_myself()
    jql = (
        f"project = {CFG.project_key} "
        f"AND sprint = {sprint_id} "
        f"AND assignee = '{me['accountId']}'"
    )
    if status:
        jql += f" AND status = '{status}'"
    jql += " ORDER BY priority DESC, created ASC"

    return search_issues(
        jql,
        fields=["summary", "status", "issuetype", "priority", "labels", "duedate"],
    )


def todo_today(sprint_id: int = None) -> list:
    """获取我今天要做的任务（To Do + In Progress）"""
    from .issue_ops import search_issues

    if not sprint_id:
        active = get_active_sprint()
        if not active:
            raise RuntimeError("No active sprint found")
        sprint_id = active["id"]

    me = get_myself()
    jql = (
        f"project = {CFG.project_key} "
        f"AND sprint = {sprint_id} "
        f"AND assignee = '{me['accountId']}' "
        f"AND status IN ('To Do', 'In Progress') "
        f"ORDER BY priority DESC"
    )
    return search_issues(
        jql,
        fields=["summary", "status", "issuetype", "priority", "labels"],
    )


def unassigned_tasks(sprint_id: int = None) -> list:
    """获取当前 Sprint 未分配的任务（领任务用）"""
    from .issue_ops import search_issues

    if not sprint_id:
        active = get_active_sprint()
        if not active:
            raise RuntimeError("No active sprint found")
        sprint_id = active["id"]

    jql = (
        f"project = {CFG.project_key} "
        f"AND sprint = {sprint_id} "
        f"AND assignee IS EMPTY "
        f"AND status = 'To Do' "
        f"ORDER BY priority DESC"
    )
    return search_issues(
        jql,
        fields=["summary", "status", "issuetype", "priority", "labels"],
    )


# ──────────────────────────────────────
# Label & Field 更新
# ──────────────────────────────────────

def add_labels(issue_key: str, labels: list):
    """给 Issue 追加 labels（不覆盖已有）"""
    result, err = jira_request("PUT", f"/issue/{issue_key}", {
        "update": {
            "labels": [{"add": label} for label in labels]
        }
    })
    if err:
        raise RuntimeError(f"add_labels failed: {err}")
    return result


def remove_labels(issue_key: str, labels: list):
    """从 Issue 移除指定 labels"""
    result, err = jira_request("PUT", f"/issue/{issue_key}", {
        "update": {
            "labels": [{"remove": label} for label in labels]
        }
    })
    if err:
        raise RuntimeError(f"remove_labels failed: {err}")
    return result


def set_story_points(issue_key: str, points: int):
    """
    设置 Story Points（通过 label 方式：sp-N）

    ⚠️ 如果项目用 label 而非 customfield 记录 SP
    先清除旧的 sp-* label，再加新的
    """
    # 获取当前 labels
    from .issue_ops import get_issue
    issue = get_issue(issue_key)
    current_labels = issue["fields"].get("labels", [])
    old_sp = [l for l in current_labels if l.startswith("sp-")]

    updates = [{"remove": l} for l in old_sp]
    updates.append({"add": f"sp-{points}"})

    result, err = jira_request("PUT", f"/issue/{issue_key}", {
        "update": {"labels": updates}
    })
    if err:
        raise RuntimeError(f"set_story_points failed: {err}")
    return result


# ──────────────────────────────────────
# 状态流转（增强版，支持模糊匹配）
# ──────────────────────────────────────

# 常见状态别名映射
_STATUS_ALIASES = {
    "todo": "To Do",
    "to do": "To Do",
    "backlog": "To Do",
    "doing": "In Progress",
    "in progress": "In Progress",
    "wip": "In Progress",
    "review": "In Review",
    "in review": "In Review",
    "done": "Done",
    "closed": "Done",
    "resolved": "Done",
}


def smart_transition(issue_key: str, target: str):
    """
    智能状态流转 — 支持模糊匹配

    Args:
        target: 目标状态，支持精确名称或别名
                e.g. "doing" → "In Progress", "done" → "Done"

    如果精确匹配失败，尝试大小写不敏感 + 别名匹配
    """
    # 先尝试别名
    normalized = _STATUS_ALIASES.get(target.lower(), target)

    transitions, err = jira_request("GET", f"/issue/{issue_key}/transitions")
    if err:
        raise RuntimeError(f"get transitions failed: {err}")

    available = transitions["transitions"]

    # 精确匹配
    tid = next((t["id"] for t in available if t["name"] == normalized), None)

    # 大小写不敏感匹配
    if not tid:
        tid = next(
            (t["id"] for t in available if t["name"].lower() == normalized.lower()),
            None,
        )

    # 包含匹配（最后手段）
    if not tid:
        tid = next(
            (t["id"] for t in available if normalized.lower() in t["name"].lower()),
            None,
        )

    if not tid:
        names = [t["name"] for t in available]
        raise ValueError(
            f"Status '{target}' (resolved: '{normalized}') not found. "
            f"Available transitions: {names}"
        )

    result, err = jira_request("POST", f"/issue/{issue_key}/transitions", {
        "transition": {"id": tid}
    })
    if err:
        raise RuntimeError(f"smart_transition failed: {err}")
    return result

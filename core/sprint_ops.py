"""
core/sprint_ops.py — Sprint 管理操作

README 中列出但原始仓库缺失，现补全。
"""
from .auth import agile_request, jira_request
from .config import CFG


def get_active_sprint(board_id: int = None) -> dict | None:
    """
    获取当前 active Sprint

    Returns:
        Sprint dict (id, name, startDate, endDate, goal) or None
    """
    bid = board_id or CFG.board_id
    result, err = agile_request("GET", f"/board/{bid}/sprint?state=active")
    if err:
        raise RuntimeError(f"get_active_sprint failed: {err}")
    sprints = result.get("values", [])
    return sprints[0] if sprints else None


def get_sprint_issues(sprint_id: int, fields: list = None, max_results: int = 100) -> list:
    """获取 Sprint 中所有 Issue"""
    f = fields or ["summary", "status", "issuetype", "priority", "assignee", "labels"]
    result, err = agile_request(
        "GET",
        f"/sprint/{sprint_id}/issue?maxResults={max_results}&fields={','.join(f)}",
    )
    if err:
        raise RuntimeError(f"get_sprint_issues failed: {err}")
    return result.get("issues", [])


def list_sprints(board_id: int = None, state: str = "active,future") -> list:
    """
    列出 Board 的 Sprint

    Args:
        state: "active", "future", "closed", 或逗号组合
    """
    bid = board_id or CFG.board_id
    result, err = agile_request("GET", f"/board/{bid}/sprint?state={state}")
    if err:
        raise RuntimeError(f"list_sprints failed: {err}")
    return result.get("values", [])


def get_sprint_report(sprint_id: int, board_id: int = None) -> dict:
    """
    获取 Sprint 报告（完成/未完成/移除的 Issue 汇总）
    ⚠️ 使用 Greenhopper API（非标准 Agile API）
    """
    bid = board_id or CFG.board_id
    # Greenhopper endpoint — works on Jira Cloud
    from .auth import jira_request as _req
    import urllib.request
    import urllib.error
    import json
    import base64
    from .config import CFG as _cfg

    auth = base64.b64encode(f"{_cfg.email}:{_cfg.token}".encode()).decode()
    url = f"{_cfg.jira_base}/rest/greenhopper/1.0/rapid/charts/sprintreport?rapidViewId={bid}&sprintId={sprint_id}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Basic {auth}",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"get_sprint_report failed: {e.read().decode()}")

"""
core/issue_ops.py — Issue CRUD 操作

Issue Type IDs 从 jira-config.json 的 issue_types 字段读取。
见 examples/jira-config.example.json
"""
import time
from .auth import jira_request, agile_request
from .config import CFG


def _get_type_id(type_name: str) -> str:
    """从配置获取 Issue Type ID，缺失时报错并给出提示"""
    if not CFG.issue_types:
        raise RuntimeError(
            f"issue_types not configured. Add issue_types to jira-config.json. "
            f"See examples/jira-config.example.json"
        )
    tid = CFG.issue_types.get(type_name)
    if not tid:
        raise RuntimeError(
            f"Issue type '{type_name}' not found in config. "
            f"Available: {list(CFG.issue_types.keys())}"
        )
    return tid

PRIORITIES = ["Highest", "High", "Medium", "Low", "Lowest"]


def create_epic(summary: str, description_adf: dict, priority: str = "High", due_date: str = None) -> str:
    """创建 Epic，返回 issue key (e.g. 'LFX-1')"""
    payload = {
        "fields": {
            "project": {"key": CFG.project_key},
            "issuetype": {"id": _get_type_id("Epic")},
            "summary": summary,
            "description": description_adf,
            "priority": {"name": priority},
        }
    }
    if due_date:
        payload["fields"]["duedate"] = due_date
    result, err = jira_request("POST", "/issue", payload)
    if err:
        raise RuntimeError(f"create_epic failed: {err}")
    return result["key"]


def create_story(summary: str, description_adf: dict, epic_key: str,
                 priority: str = "High", due_date: str = None) -> str:
    """
    创建 Story，挂载到 Epic 下（使用 parent 字段）
    Epic→Story 层级差为1，支持 parent 字段直接关联
    """
    payload = {
        "fields": {
            "project": {"key": CFG.project_key},
            "issuetype": {"id": _get_type_id("Story")},
            "summary": summary,
            "description": description_adf,
            "priority": {"name": priority},
            "parent": {"key": epic_key},  # ✅ Epic→Story 可用 parent
        }
    }
    if due_date:
        payload["fields"]["duedate"] = due_date
    result, err = jira_request("POST", "/issue", payload)
    if err:
        raise RuntimeError(f"create_story failed: {err}")
    return result["key"]


def create_feature(summary: str, description_adf: dict, epic_key: str,
                   issue_type: str = "Feature", priority: str = "High",
                   due_date: str = None, labels: list = None) -> str:
    """
    创建 Feature/Task/Bug/Fix，并设置 Epic Link
    ⚠️ Feature 和 Story 同为 level 0，不能用 parent 关联 Story
       需要后续调用 link_ops.link_feature_to_story()
    """
    payload = {
        "fields": {
            "project": {"key": CFG.project_key},
            "issuetype": {"id": _get_type_id(issue_type)},
            "summary": summary,
            "description": description_adf,
            "priority": {"name": priority},
            "customfield_10014": epic_key,  # Epic Link（Classic 项目专用）
        }
    }
    if due_date:
        payload["fields"]["duedate"] = due_date
    if labels:
        payload["fields"]["labels"] = labels
    result, err = jira_request("POST", "/issue", payload)
    if err:
        raise RuntimeError(f"create_feature failed: {err}")
    return result["key"]


def add_to_sprint(issue_keys: list, sprint_id: int = None):
    """
    将 Issues 加入 Sprint
    ⚠️ 创建 Issue 后必须手动调用此函数，Issue 不会自动归入 Sprint
    ⚠️ 必须用 agile API（/rest/agile/1.0/），不是 /rest/api/3/
    ⚠️ sprint_id 不传时自动获取 active sprint
    """
    if sprint_id is None:
        from .sprint_ops import get_active_sprint
        active = get_active_sprint()
        if not active:
            raise RuntimeError("No active sprint found and no sprint_id provided")
        sprint_id = active["id"]
    result, err = agile_request("POST", f"/sprint/{sprint_id}/issue", {
        "issues": issue_keys
    })
    if err:
        raise RuntimeError(f"add_to_sprint failed: {err}")
    return result


def update_status(issue_key: str, target_status: str):
    """更新 Issue 状态（通过 transitions）"""
    transitions, err = jira_request("GET", f"/issue/{issue_key}/transitions")
    if err:
        raise RuntimeError(f"get transitions failed: {err}")
    tid = next(
        (t["id"] for t in transitions["transitions"] if t["name"] == target_status),
        None
    )
    if not tid:
        available = [t["name"] for t in transitions["transitions"]]
        raise ValueError(f"Status '{target_status}' not found. Available: {available}")
    result, err = jira_request("POST", f"/issue/{issue_key}/transitions", {
        "transition": {"id": tid}
    })
    if err:
        raise RuntimeError(f"update_status failed: {err}")
    return result


def get_issue(issue_key: str) -> dict:
    """获取 Issue 详情"""
    result, err = jira_request("GET", f"/issue/{issue_key}")
    if err:
        raise RuntimeError(f"get_issue failed: {err}")
    return result


def search_issues(jql: str, fields: list = None, max_results: int = 50) -> list:
    """
    搜索 Issues（JQL）
    ⚠️ 使用 POST /search/jql（旧版 GET /search?jql= 已废弃）
    """
    payload = {
        "jql": jql,
        "maxResults": max_results,
        "fields": fields or ["summary", "status", "issuetype", "priority", "assignee", "labels"],
    }
    result, err = jira_request("POST", "/search/jql", payload)
    if err:
        raise RuntimeError(f"search_issues failed: {err}")
    return result.get("issues", [])


def bulk_update_descriptions(descriptions: dict, delay: float = 0.3):
    """
    批量更新 Issue 描述（ADF 格式）
    
    Args:
        descriptions: {issue_key: adf_doc} 字典
        delay: 请求间隔（秒），避免触发限流
    """
    results = []
    for issue_key, desc in descriptions.items():
        result, err = jira_request("PUT", f"/issue/{issue_key}", {
            "fields": {"description": desc}
        })
        if err:
            print(f"❌ {issue_key}: {err[:100]}")
            results.append((issue_key, False, err))
        else:
            print(f"✅ {issue_key}: updated")
            results.append((issue_key, True, None))
        time.sleep(delay)
    return results

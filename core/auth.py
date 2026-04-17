"""
core/auth.py — Jira API 认证 & 基础客户端

配置从 core.config 集中读取。
"""
import urllib.request
import urllib.error
import json
import base64

from .config import CFG

auth = base64.b64encode(f"{CFG.email}:{CFG.token}".encode()).decode()


def jira_request(method: str, path: str, data: dict = None):
    """
    Jira REST API v3 请求

    Args:
        method: HTTP method (GET/POST/PUT/DELETE)
        path: API path, e.g. "/issue/LFX-1"
        data: Request body (will be JSON-encoded)

    Returns:
        (response_dict, error_string) — error is None on success

    Notes:
        - 使用 POST /search/jql 替代已废弃的 GET /search?jql=
        - 描述字段必须使用 ADF 格式（见 templates/adf_builder.py）
        - 204 No Content 返回空 dict
    """
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        f"{CFG.jira_base}/rest/api/3{path}",
        data=body,
        method=method,
        headers={
            "Authorization": f"Basic {auth}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read()
            return json.loads(content) if content else {}, None
    except urllib.error.HTTPError as e:
        return None, e.read().decode()


def agile_request(method: str, path: str, data: dict = None):
    """
    Jira Agile API (Sprint 操作专用)

    ⚠️ Sprint 操作必须用此函数，路径前缀为 /rest/agile/1.0/
    普通 /rest/api/3/ 不支持 Sprint API。

    常用路径:
        POST /sprint/{id}/issue  — 将 issues 加入 Sprint
        GET  /board/{id}/sprint  — 列出 Board 的 Sprint
    """
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        f"{CFG.jira_base}/rest/agile/1.0{path}",
        data=body,
        method=method,
        headers={
            "Authorization": f"Basic {auth}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read()
            return json.loads(content) if content else {}, None
    except urllib.error.HTTPError as e:
        return None, e.read().decode()

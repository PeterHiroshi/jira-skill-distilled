"""
core/attachment_ops.py — 文件附件上传

规则：
  PRD 等产品文档  → 上传到对应 Epic issue
  设计稿/原型     → 上传到 Feature issue
  测试报告        → 上传到 Task issue
"""
import urllib.request
import urllib.error
import mimetypes
import base64
import json
import os

from .config import CFG

auth = base64.b64encode(f"{CFG.email}:{CFG.token}".encode()).decode()


def upload_attachment(issue_key: str, file_path: str) -> dict:
    """
    上传文件到 Jira issue 附件
    
    Args:
        issue_key: e.g. "LFX-1"
        file_path: 本地文件路径
    
    Returns:
        附件信息 dict（response[0]）
    
    ⚠️ 必须带 X-Atlassian-Token: no-check，否则返回 403 XSRF error
    ⚠️ boundary 字符串不能含特殊字符（如 =）
    ⚠️ 响应是 JSON 数组，用 result[0] 取第一个附件
    """
    filename = os.path.basename(file_path)
    mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    boundary = "----JiraFileBoundary7x9k"
    with open(file_path, "rb") as f:
        file_content = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode() + file_content + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        f"{CFG.jira_base}/rest/api/3/issue/{issue_key}/attachments",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Basic {auth}",
            "X-Atlassian-Token": "no-check",   # ⚠️ 关键：必须带此 header
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            return result[0]  # ⚠️ 响应是数组
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"upload_attachment failed: {e.read().decode()}")

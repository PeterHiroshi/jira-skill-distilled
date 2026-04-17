"""
core/link_ops.py — Issue 关联操作

关联规则图谱：
    Epic
      └─[Epic Link customfield_10014]─► Feature/Story/Task
      └─[Polaris work item link: implements]─► Feature

    Feature/Story
      └─[Blocks]─► Improvement
      └─[Relates]─► Bug

    Bug
      └─[Blocks]─► Fix

    Fix └─[Blocks]─► Docs/Release Task
"""
from .auth import jira_request


def link_feature_to_story(feature_key: str, story_key: str):
    """
    Feature 实现 Story 的关联（Polaris work item link）
    
    方向关键：
      - inward = Story  → Story 页面显示 "is implemented by ← Feature" ✅
      - outward = Feature → Feature 页面显示 "implements → Story" ✅
    
    ⚠️ 不要用 parent 字段！Feature 和 Story 同为 level 0，parent 会报错。
    """
    result, err = jira_request("POST", "/issueLink", {
        "type": {"name": "Polaris work item link"},
        "inwardIssue": {"key": story_key},    # Story: "is implemented by"
        "outwardIssue": {"key": feature_key}, # Feature: "implements"
    })
    if err:
        raise RuntimeError(f"link_feature_to_story failed: {err}")
    return result


def link_blocks(blocker_key: str, blocked_key: str):
    """
    设置阻塞关系：blocker_key 阻塞 blocked_key
    
    常见用法：
        Bug 阻塞 Fix: link_blocks("LFX-23", "LFX-24")
        Feature 阻塞 Improvement: link_blocks("LFX-11", "LFX-12")
    """
    result, err = jira_request("POST", "/issueLink", {
        "type": {"name": "Blocks"},
        "inwardIssue": {"key": blocker_key},  # "is blocked by"
        "outwardIssue": {"key": blocked_key}, # "blocks"
    })
    if err:
        raise RuntimeError(f"link_blocks failed: {err}")
    return result


def link_relates(key1: str, key2: str):
    """
    设置普通关联关系（双向 Relates）
    用于：Feature ↔ Bug 关联（发现缺陷时）
    """
    result, err = jira_request("POST", "/issueLink", {
        "type": {"name": "Relates"},
        "inwardIssue": {"key": key1},
        "outwardIssue": {"key": key2},
    })
    if err:
        raise RuntimeError(f"link_relates failed: {err}")
    return result


def set_epic_link(child_key: str, epic_key: str):
    """
    将子 Issue 挂到 Epic（Classic 项目专用）
    使用 customfield_10014（Epic Link 自定义字段）
    
    ⚠️ 仅适用于 Classic/Company-Managed 项目
       Next-gen 项目不支持此字段，用 link_relates() 替代
    """
    result, err = jira_request("PUT", f"/issue/{child_key}", {
        "fields": {"customfield_10014": epic_key}
    })
    if err:
        raise RuntimeError(f"set_epic_link failed: {err}")
    return result


def add_comment(issue_key: str, text: str):
    """添加 Comment（记录会议决策/standup 结论）"""
    result, err = jira_request("POST", f"/issue/{issue_key}/comment", {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [{
                "type": "paragraph",
                "content": [{"type": "text", "text": text}]
            }]
        }
    })
    if err:
        raise RuntimeError(f"add_comment failed: {err}")
    return result

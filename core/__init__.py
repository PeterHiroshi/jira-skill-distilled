"""
core/__init__.py — Public API surface
"""
from .config import CFG
from .auth import jira_request, agile_request
from .issue_ops import (
    create_epic, create_story, create_feature,
    add_to_sprint, update_status, get_issue, search_issues,
)
from .sprint_ops import (
    get_active_sprint, get_sprint_issues, list_sprints,
)
from .dev_ops import (
    get_myself, find_user, assign_issue, assign_to_me,
    add_worklog, get_worklogs, get_comments,
    my_sprint_tasks, todo_today, unassigned_tasks,
    add_labels, remove_labels, set_story_points,
    smart_transition,
)
from .link_ops import (
    link_feature_to_story, link_blocks, link_relates,
    set_epic_link, add_comment,
)
from .attachment_ops import upload_attachment

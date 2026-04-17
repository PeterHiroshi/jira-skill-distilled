"""
core/config.py — 项目配置（集中管理，不再硬编码）

使用方式：
    from core.config import CFG
    CFG.project_key  # "LFX"
    CFG.jira_base    # "https://icestonetech.atlassian.net"

支持环境变量覆盖：
    JIRA_BASE, JIRA_EMAIL, JIRA_PROJECT_KEY, JIRA_BOARD_ID
"""
import os


class JiraConfig:
    def __init__(self):
        self.jira_base = os.environ.get("JIRA_BASE", "https://icestonetech.atlassian.net")
        self.email = os.environ.get("JIRA_EMAIL", "peter.ma@icestonetech.com")
        self.project_key = os.environ.get("JIRA_PROJECT_KEY", "LFX")
        self.board_id = int(os.environ.get("JIRA_BOARD_ID", "35"))

        # Token: env var > file
        self.token = os.environ.get("JIRA_TOKEN") or self._read_token_file()

    @staticmethod
    def _read_token_file() -> str:
        path = os.path.expanduser("~/.hermes/secrets/jira_token")
        try:
            return open(path).read().strip()
        except FileNotFoundError:
            raise RuntimeError(
                f"Jira token not found. Set JIRA_TOKEN env var or create {path}"
            )


CFG = JiraConfig()

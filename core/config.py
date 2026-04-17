"""
core/config.py — Jira 项目配置（零耦合，配置文件驱动）

加载优先级（每个字段独立）：
    1. 环境变量 (JIRA_BASE, JIRA_EMAIL, JIRA_PROJECT_KEY, JIRA_BOARD_ID, JIRA_TOKEN)
    2. 配置文件 jira-config.json（skill 目录或 cwd）
    3. 无默认值 — 缺失则报错，强制用户显式配置

配置文件示例见 examples/jira-config.example.json

向后兼容：
    - 旧的 ~/.hermes/secrets/jira_token 路径仍会检查
    - 环境变量优先级最高，已有部署不受影响
"""
import os
import json

_SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Token 候选路径（按优先级）
_TOKEN_PATHS = [
    os.path.join(_SKILL_DIR, "secrets", "jira_token"),   # skill 本地
    os.path.expanduser("~/.config/jira/token"),           # XDG 标准
    os.path.expanduser("~/.jira/token"),                  # 通用
    os.path.expanduser("~/.hermes/secrets/jira_token"),   # 向后兼容 Hermes
]


def _load_config_file() -> dict:
    """尝试从 jira-config.json 加载配置"""
    candidates = [
        os.path.join(_SKILL_DIR, "jira-config.json"),
        os.path.join(os.getcwd(), "jira-config.json"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            with open(path) as f:
                return json.load(f)
    return {}


def _find_token() -> str | None:
    """按优先级搜索 token 文件"""
    for path in _TOKEN_PATHS:
        if os.path.isfile(path):
            return open(path).read().strip()
    return None


class JiraConfig:
    def __init__(self):
        file_cfg = _load_config_file()

        self.jira_base = (
            os.environ.get("JIRA_BASE")
            or file_cfg.get("jira_base")
        )
        self.email = (
            os.environ.get("JIRA_EMAIL")
            or file_cfg.get("email")
        )
        self.project_key = (
            os.environ.get("JIRA_PROJECT_KEY")
            or file_cfg.get("project_key")
        )
        self.board_id = (
            int(os.environ["JIRA_BOARD_ID"]) if "JIRA_BOARD_ID" in os.environ
            else file_cfg.get("board_id")
        )
        self.token = (
            os.environ.get("JIRA_TOKEN")
            or file_cfg.get("token")
            or _find_token()
        )

        # Issue Type IDs — 项目相关，从配置文件读取
        self.issue_types = file_cfg.get("issue_types", {})

    def require(self, *fields):
        """校验必填字段，缺失时给出明确提示"""
        missing = [f for f in fields if not getattr(self, f, None)]
        if missing:
            raise RuntimeError(
                f"Jira config missing: {', '.join(missing)}. "
                f"Set via environment variables (JIRA_BASE, JIRA_EMAIL, etc.) "
                f"or create jira-config.json. See examples/jira-config.example.json"
            )


CFG = JiraConfig()

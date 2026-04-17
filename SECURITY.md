# Security

## Credentials

- Jira API Token — 通过以下方式之一配置（优先级从高到低）：
  1. 环境变量 `JIRA_TOKEN`
  2. `jira-config.json` 中的 `token` 字段
  3. Token 文件：`secrets/jira_token`、`~/.config/jira/token`、`~/.jira/token`

## 安全实践

```python
# ✅ 使用环境变量
import os
TOKEN = os.environ["JIRA_TOKEN"]

# ✅ 使用 config（自动处理）
from core.config import CFG
# CFG.token 已按优先级加载

# ❌ 不要硬编码 token
TOKEN = "atatt_xxx..."  # NEVER DO THIS
```

## .gitignore

确保以下文件不会被提交：
- `jira-config.json`（含 token）
- `secrets/`

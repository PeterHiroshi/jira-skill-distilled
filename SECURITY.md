# ⚠️ 安全说明

此仓库为**私有（Private）**仓库。以下信息**不应提交**到 Git：

- Jira API Token（保存在 `~/.hermes/secrets/jira_token`）
- GitHub PAT Token
- 任何明文密码或密钥

代码中通过读取本地文件获取 Token：
```python
TOKEN = open(os.path.expanduser("~/.hermes/secrets/jira_token")).read().strip()
```

如需分享代码，请先移除所有敏感信息。

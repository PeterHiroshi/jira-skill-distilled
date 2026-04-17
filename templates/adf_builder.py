"""
templates/adf_builder.py — Atlassian Document Format 构造器

⚠️ Jira 描述字段必须使用 ADF 格式（纯文本会被拒绝）
"""


def adf(paragraphs: list) -> dict:
    """
    从 (type, content) 元组列表构建 ADF 文档
    
    type 支持:
        'h2'   — 二级标题
        'h3'   — 三级标题
        'p'    — 段落文本
        'ul'   — 无序列表 (content 为 list[str])
        'code' — 代码块 (content 为 str)
    
    示例:
        doc = adf([
            ('h2', '战略背景'),
            ('p', '本 Epic 旨在...'),
            ('h2', '验收标准'),
            ('ul', ['✅ API 响应时间 < 200ms', '✅ 覆盖率 > 80%']),
            ('code', 'POST /api/v1/proofs'),
        ])
    """
    content = []
    for t, txt in paragraphs:
        if t == "h2":
            content.append({
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": txt}],
            })
        elif t == "h3":
            content.append({
                "type": "heading",
                "attrs": {"level": 3},
                "content": [{"type": "text", "text": txt}],
            })
        elif t == "p":
            content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": txt}],
            })
        elif t == "ul":
            items = [
                {
                    "type": "listItem",
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": item}],
                    }],
                }
                for item in txt
            ]
            content.append({"type": "bulletList", "content": items})
        elif t == "code":
            content.append({
                "type": "codeBlock",
                "attrs": {"language": "text"},
                "content": [{"type": "text", "text": txt}],
            })
    return {"type": "doc", "version": 1, "content": content}


# === 推荐结构模板 ===

def epic_description(background: str, user_story: str, includes: list,
                     excludes: list, tech_arch: str, acceptance_criteria: list) -> dict:
    """Epic 描述模板：战略背景 → 用户故事 → 范围 → 技术架构 → 验收标准"""
    return adf([
        ("h2", "战略背景"),
        ("p", background),
        ("h2", "用户故事"),
        ("p", user_story),
        ("h2", "范围"),
        ("h3", "✅ 包含"),
        ("ul", includes),
        ("h3", "❌ 不包含"),
        ("ul", excludes),
        ("h2", "技术架构"),
        ("p", tech_arch),
        ("h2", "验收标准"),
        ("ul", acceptance_criteria),
    ])


def story_description(user_story: str, business_value: str,
                      acceptance_criteria: list, feature_mapping: list) -> dict:
    """Story 描述模板：用户故事 → 业务价值 → 验收标准 → Feature 映射"""
    return adf([
        ("h2", "用户故事"),
        ("p", user_story),
        ("h2", "业务价值"),
        ("p", business_value),
        ("h2", "验收标准"),
        ("ul", acceptance_criteria),
        ("h2", "实现 Feature 映射"),
        ("ul", feature_mapping),
    ])


def feature_description(objective: str, tech_spec: str,
                        dependencies: list, acceptance_criteria: list) -> dict:
    """Feature/Task 描述模板：任务目标 → 技术规格 → 依赖 → 验收标准"""
    return adf([
        ("h2", "任务目标"),
        ("p", objective),
        ("h2", "技术规格"),
        ("code", tech_spec),
        ("h2", "依赖"),
        ("ul", dependencies),
        ("h2", "验收标准"),
        ("ul", acceptance_criteria),
    ])

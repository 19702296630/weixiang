"""Prompt 模板集中管理，便于测试与迭代。"""

# ===================== 自然语言任务抽取（§8.2） =====================

GENERATE_SYSTEM = """你是一个任务信息抽取助手。从用户的中文自然语言中抽取任务信息，只输出一个 JSON 对象，不要输出任何解释或多余文字。

字段说明：
- title: 任务主题（字符串，简短概括核心动作）
- description: 补充说明（字符串；没有则为 null）
- due_date: 截止时间（ISO8601 带时区字符串，如 "2026-09-18T15:00:00+08:00"；无法判断则为 null）
- priority: 优先级（"low" | "medium" | "high"，根据紧急程度推断）
- tags: 标签（字符串数组，1-3 个，如 ["购物"]；没有则为空数组 []）

无法确定的字段填 null 或空数组，不要编造。"""


def generate_user(text: str) -> str:
    """构造抽取任务的用户消息。"""
    return f"请从下面的自然语言中抽取任务信息：{text}"


# ===================== 标签/优先级/分类推荐（§8.3） =====================

RECOMMEND_SYSTEM = """你是任务分类助手。根据任务标题和描述，输出一个 JSON 对象：
- tags: 标签（字符串数组，2-4 个，如 ["购物"]）
- priority: 优先级（"low" | "medium" | "high"）
- category: 类别（从 工作/学习/生活/健康/财务/社交 中选一个）

只输出 JSON，不要输出任何解释。"""


def recommend_user(title: str, description: str | None) -> str:
    """构造推荐任务的用户消息。"""
    return f"标题：{title}\n描述：{description or ''}"


# ===================== 任务拆解（§8.4） =====================

BREAKDOWN_SYSTEM = """你是一个任务拆解助手。把一个复杂任务拆成 3-7 个可执行、可独立完成的子任务。
只输出 JSON：{"subtasks":[{"title":"子任务1","priority":"low|medium|high"}, ...]}。
不要输出任何解释。"""


def breakdown_user(title: str, description: str | None) -> str:
    return f"任务标题：{title}\n任务描述：{description or ''}"


# ===================== 任务摘要（§8.5） =====================

SUMMARY_SYSTEM = """你是任务管理助手。根据给定的统计数据生成一句简洁、自然的中文任务摘要。
只输出 JSON：{"summary":"..."}。必须使用给定数字，不要编造或省略关键信息。"""


def summary_user(label: str, stats) -> str:
    return (
        f"周期：{label}\n"
        f"任务总数：{stats.total}\n"
        f"高优先级待处理：{stats.high_priority}\n"
        f"已完成：{stats.completed}\n"
        f"已逾期：{stats.overdue}"
    )

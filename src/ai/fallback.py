"""降级规则引擎：LLM 不可用时的关键词/规则兜底（不依赖网络）。

作为「最后一道保险」，保证任何 AI 功能在 LLM 失败时仍能返回合理结果。
"""
from datetime import datetime

from src.models.schemas import TaskDraft
from src.models.task import TaskPriority
from src.utils.time import parse_datetime

# 关键词 → 标签（命中即推荐，顺序即优先级）
_TAG_KEYWORDS: dict[str, list[str]] = {
    "购物": ["买", "采购", "超市", "购物", "下单", "日用品", "快递"],
    "工作": ["报告", "开会", "会议", "项目", "邮件", "汇报", "文档", "需求", "上线"],
    "学习": ["学习", "复习", "背单词", "课程", "作业", "考试", "读书", "看书", "笔记"],
    "健康": ["健身", "跑步", "体检", "吃药", "医院", "锻炼", "运动", "复诊"],
    "生活": ["打扫", "洗衣", "做饭", "房租", "水电", "收拾", "家务", "缴费"],
    "财务": ["还款", "账单", "报销", "转账", "理财", "工资"],
    "社交": ["生日", "聚会", "拜访", "婚礼", "邀请", "聚餐", "见面"],
}

_HIGH_PRIORITY_KEYWORDS = ["紧急", "立刻", "马上", "尽快", "重要", "截止", "必须", "务必", "抓紧"]
_LOW_PRIORITY_KEYWORDS = ["有空", "不急", "随便", "抽空", "以后", "改天", "闲暇", "再说"]

_CATEGORIES = {"工作", "学习", "生活", "健康", "财务", "社交"}


def recommend_tags(title: str, description: str | None = None) -> list[str]:
    """按关键词命中推荐标签，最多 3 个。"""
    text = f"{title} {description or ''}"
    tags = [tag for tag, keywords in _TAG_KEYWORDS.items() if any(k in text for k in keywords)]
    return tags[:3]


def recommend_priority(
    title: str,
    description: str | None = None,
    due_date: datetime | None = None,
) -> TaskPriority:
    """关键词 + 截止时间距离综合推断优先级。"""
    text = f"{title} {description or ''}"
    if any(k in text for k in _HIGH_PRIORITY_KEYWORDS):
        return TaskPriority.high
    if any(k in text for k in _LOW_PRIORITY_KEYWORDS):
        return TaskPriority.low
    if due_date is not None:
        hours_left = (due_date - datetime.now()).total_seconds() / 3600
        if hours_left < 24:
            return TaskPriority.high
        if hours_left < 72:
            return TaskPriority.medium
    return TaskPriority.medium


def recommend_category(title: str, description: str | None = None) -> str:
    """从命中的标签里取第一个属于预定义类别的作为分类，否则默认「生活」。"""
    for tag in recommend_tags(title, description):
        if tag in _CATEGORIES:
            return tag
    return "生活"


def generate_fallback(text: str) -> TaskDraft:
    """LLM 失败时，用规则从自然语言里抽一个尽量可用的草稿。"""
    due_date = parse_datetime(text)
    return TaskDraft(
        title=text,
        description=None,
        priority=recommend_priority(text, due_date=due_date),
        tags=recommend_tags(text) or None,
        due_date=due_date,
        source="fallback",
    )

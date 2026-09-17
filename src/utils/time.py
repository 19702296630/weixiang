"""时间表达式解析（规则版）：作为 LLM 失败时的降级兜底。

支持：今天/明天/后天/大后天、下周X、X 小时/分钟/天/周后、以及
「下午3点」「15:30」等具体时刻。无法解析时返回 None。
"""
import re
from datetime import datetime, timedelta

_WEEKDAY_NUM = {
    "一": 0,
    "二": 1,
    "三": 2,
    "四": 3,
    "五": 4,
    "六": 5,
    "日": 6,
    "天": 6,
}


def _parse_time_of_day(text: str) -> tuple[int, int] | None:
    """解析具体时刻，返回 (时, 分) 或 None。"""
    # 24 小时制：HH:MM
    m = re.search(r"(\d{1,2})[:：](\d{1,2})", text)
    if m:
        hour, minute = int(m.group(1)), int(m.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return hour, minute

    # 中文时刻：上午/下午/晚上/中午 + N点(半/一刻/三刻)
    m = re.search(r"(上午|下午|晚上|中午|凌晨|早上|傍晚)?\s*(\d{1,2})点(半|一刻|三刻)?", text)
    if m:
        period, hour, frac = m.group(1), int(m.group(2)), m.group(3)
        minute = {"半": 30, "一刻": 15, "三刻": 45}.get(frac, 0)
        if period in ("下午", "晚上", "傍晚") and hour < 12:
            hour += 12
        if period == "中午" and hour < 12:
            hour += 12
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return hour, minute
    return None


def parse_datetime(text: str, now: datetime | None = None) -> datetime | None:
    """从中文时间表达解析出一个朴素 datetime；无法解析返回 None。"""
    if now is None:
        now = datetime.now().replace(second=0, microsecond=0)

    # 1) 相对时长：X 小时/分钟/天/周 后
    rel = re.search(r"(\d+)\s*(?:个)?(小时|分钟|天|周)后", text)
    if rel:
        n = int(rel.group(1))
        delta = {
            "小时": timedelta(hours=n),
            "分钟": timedelta(minutes=n),
            "天": timedelta(days=n),
            "周": timedelta(weeks=n),
        }[rel.group(2)]
        return now + delta

    # 2) 具体时刻
    time_of_day = _parse_time_of_day(text)

    # 3) 日期基准：周X / 下周X，否则今天/明天/后天/大后天
    has_date = False
    base = now

    week = re.search(r"(下|本|这)?\s*(?:周|星期|礼拜)([一二三四五六日天])", text)
    if week:
        target = _WEEKDAY_NUM[week.group(2)]
        days_ahead = (target - now.weekday()) % 7
        if week.group(1) == "下":
            days_ahead += 7
        base = now + timedelta(days=days_ahead)
        has_date = True
    else:
        day_offset = None
        if "大后天" in text:
            day_offset = 3
        elif "后天" in text:
            day_offset = 2
        elif "明天" in text:
            day_offset = 1
        elif "今天" in text:
            day_offset = 0
        if day_offset is not None:
            base = now + timedelta(days=day_offset)
            has_date = True

    # 4) 组合：有具体时刻覆盖时分，否则沿用日期基准
    if time_of_day is not None:
        return base.replace(hour=time_of_day[0], minute=time_of_day[1])
    if has_date:
        return base
    return None

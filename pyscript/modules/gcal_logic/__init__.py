def greeting(hour: int) -> str:
    if 4 <= hour < 12:
        return "おはようございます。"
    if 12 <= hour < 17:
        return "こんにちわ。"
    return "こんばんわ。"


def format_hhmm(dt) -> str:
    return dt.strftime("%H時%M分")


def _group_and_sort(events: list[dict]) -> list[str]:
    groups: dict[tuple[str, str], list[str]] = {}
    for ev in events:
        evtime = " 終日 " if ev["all_day"] else format_hhmm(ev["start"]) + "から"
        key = (evtime, ev["summary"])
        groups.setdefault(key, []).append(ev["account_name"])
    lines = [
        evtime + "、".join(names) + "の" + title
        for (evtime, title), names in groups.items()
    ]
    return sorted(lines)


def format_announcement(events: list[dict], now, fetch_failed: bool = False) -> str:
    header = "　" + greeting(now.hour) + format_hhmm(now) + "になりました。"
    if fetch_failed:
        tail = "予定の取得に失敗しました。"
    elif not events:
        tail = "ありません。"
    else:
        tail = "、".join(_group_and_sort(events)) + "です。"
    return header + "今日の予定は、" + tail

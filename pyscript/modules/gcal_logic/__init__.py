from datetime import datetime


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


def normalize_event(account_name: str, raw: dict) -> dict:
    start = raw["start"]
    if "date" in start:
        all_day = True
        start_dt = datetime.fromisoformat(start["date"])
    else:
        all_day = False
        start_dt = datetime.fromisoformat(start["dateTime"])
    summary = raw.get("summary") or "予定"
    return {
        "account_name": account_name,
        "summary": summary,
        "start": start_dt,
        "all_day": all_day,
    }


def fetch_events(accounts: dict, start, end, get_events_fn) -> tuple:
    events = []
    skipped = []
    for name, entity_id in accounts.items():
        try:
            raw_events = get_events_fn(entity_id, start, end)
        except Exception:
            skipped.append(name)
            continue
        events.extend(normalize_event(name, raw) for raw in raw_events)
    return events, skipped


def is_total_failure(target_account_names: set, skipped_accounts: list, events: list) -> bool:
    return not events and set(skipped_accounts) == set(target_account_names)

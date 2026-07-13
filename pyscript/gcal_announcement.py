from datetime import datetime

from pyscript.modules import gcal_logic

ACCOUNTS = {
    "息子": "calendar.example_son",
    "娘": "calendar.example_daughter",
    "ママ": "calendar.example_mother",
    "パパ": "calendar.example_father",
}


def _get_events_for_account(entity_id, start, end):
    # NOTE: pyscriptの calendar.get_events レスポンス形式(response_variable経由で
    # 返る辞書のキー構造)を、実際にHACS導入後にログ出力して確認し、
    # 下記のインデックス([entity_id]["events"]の部分)が正しいことを検証すること。
    result = calendar.get_events(
        entity_id=entity_id,
        start_date_time=start.isoformat(),
        end_date_time=end.isoformat(),
    )
    return result[entity_id]["events"]


def _today_range():
    now = datetime.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=23, minute=59, second=59, microsecond=0)
    return now, start, end


@service
def fetch_events():
    _, start, end = _today_range()
    events, skipped_accounts = gcal_logic.fetch_events(
        ACCOUNTS, start, end, _get_events_for_account
    )
    return {"events": events, "skipped_accounts": skipped_accounts}


@service
def notify_on_failure(skipped_accounts=None):
    if not skipped_accounts:
        return
    title, message = gcal_logic.build_failure_notification(skipped_accounts)
    persistent_notification.create(title=title, message=message)


@service(supports_response="only")
def build_daily_announcement():
    now, start, end = _today_range()
    events, skipped_accounts = gcal_logic.fetch_events(
        ACCOUNTS, start, end, _get_events_for_account
    )
    if skipped_accounts:
        notify_on_failure(skipped_accounts=skipped_accounts)
    fetch_failed = gcal_logic.is_total_failure(set(ACCOUNTS.keys()), skipped_accounts, events)
    message = gcal_logic.format_announcement(events, now, fetch_failed=fetch_failed)
    return {"message": message}

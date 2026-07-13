from datetime import datetime

import gcal_logic


def _get_events_for_account(entity_id, start, end):
    # NOTE: return_response=Trueで返るレスポンスの実際のキー構造
    # ([entity_id]["events"]という想定が正しいか)を、実際にHACS導入後に
    # ログ出力して確認し、検証すること。
    result = calendar.get_events(
        entity_id=entity_id,
        start_date_time=start.isoformat(),
        end_date_time=end.isoformat(),
        return_response=True,
    )
    return result[entity_id]["events"]


def _today_range():
    now = datetime.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=23, minute=59, second=59, microsecond=0)
    return now, start, end


@service(supports_response="only")
def fetch_events(accounts):
    _, start, end = _today_range()
    events, skipped_accounts = gcal_logic.fetch_events(
        accounts, start, end, _get_events_for_account
    )
    return {"events": events, "skipped_accounts": skipped_accounts}


@service
def notify_on_failure(skipped_accounts=None):
    if not skipped_accounts:
        return
    title, message = gcal_logic.build_failure_notification(skipped_accounts)
    persistent_notification.create(title=title, message=message)


@service(supports_response="only")
def build_daily_announcement(accounts):
    now, start, end = _today_range()
    events, skipped_accounts = gcal_logic.fetch_events(
        accounts, start, end, _get_events_for_account
    )
    if skipped_accounts:
        notify_on_failure(skipped_accounts=skipped_accounts)
    fetch_failed = gcal_logic.is_total_failure(set(accounts.keys()), skipped_accounts, events)
    message = gcal_logic.format_announcement(events, now, fetch_failed=fetch_failed)
    return {"message": message}

from datetime import datetime
from pyscript.modules.gcal_logic import greeting, format_hhmm, format_announcement
from pyscript.modules.gcal_logic import normalize_event, fetch_events, is_total_failure


def test_greeting_morning():
    assert greeting(4) == "おはようございます。"
    assert greeting(11) == "おはようございます。"


def test_greeting_noon():
    assert greeting(12) == "こんにちわ。"
    assert greeting(16) == "こんにちわ。"


def test_greeting_evening():
    assert greeting(17) == "こんばんわ。"
    assert greeting(3) == "こんばんわ。"


def test_format_hhmm_zero_padded():
    assert format_hhmm(datetime(2026, 7, 13, 8, 5)) == "08時05分"


def test_format_hhmm_afternoon():
    assert format_hhmm(datetime(2026, 7, 13, 18, 30)) == "18時30分"


def test_format_announcement_no_events():
    now = datetime(2026, 7, 13, 8, 30)
    result = format_announcement([], now)
    assert result == "　おはようございます。08時30分になりました。今日の予定は、ありません。"


def test_format_announcement_single_event():
    now = datetime(2026, 7, 13, 8, 30)
    events = [
        {"account_name": "息子", "summary": "塾", "start": datetime(2026, 7, 13, 18, 55), "all_day": False},
    ]
    result = format_announcement(events, now)
    assert result == "　おはようございます。08時30分になりました。今日の予定は、18時55分から息子の塾です。"


def test_format_announcement_groups_same_time_and_title():
    now = datetime(2026, 7, 13, 8, 30)
    events = [
        {"account_name": "パパ", "summary": "歯医者", "start": datetime(2026, 7, 24, 19, 0), "all_day": False},
        {"account_name": "娘", "summary": "歯医者", "start": datetime(2026, 7, 24, 19, 0), "all_day": False},
    ]
    result = format_announcement(events, now)
    assert result == "　おはようございます。08時30分になりました。今日の予定は、19時00分からパパ、娘の歯医者です。"


def test_format_announcement_all_day_event():
    now = datetime(2026, 7, 13, 8, 30)
    events = [
        {"account_name": "娘", "summary": "バイト　書類提出", "start": datetime(2026, 7, 14), "all_day": True},
    ]
    result = format_announcement(events, now)
    assert result == "　おはようございます。08時30分になりました。今日の予定は、 終日 娘のバイト　書類提出です。"


def test_format_announcement_sorts_multiple_lines():
    now = datetime(2026, 7, 13, 8, 30)
    events = [
        {"account_name": "パパ", "summary": "会議", "start": datetime(2026, 7, 13, 20, 0), "all_day": False},
        {"account_name": "息子", "summary": "塾", "start": datetime(2026, 7, 13, 9, 0), "all_day": False},
    ]
    result = format_announcement(events, now)
    # "09時00分から息子の塾" と "20時00分からパパの会議" を文字列順にソートして連結
    assert result == (
        "　おはようございます。08時30分になりました。今日の予定は、"
        "09時00分から息子の塾、20時00分からパパの会議です。"
    )


def test_format_announcement_fetch_failed_overrides_events():
    now = datetime(2026, 7, 13, 8, 30)
    result = format_announcement([], now, fetch_failed=True)
    assert result == "　おはようございます。08時30分になりました。今日の予定は、予定の取得に失敗しました。"


def test_normalize_event_timed():
    raw = {
        "start": {"dateTime": "2026-07-13T18:55:00+09:00"},
        "end": {"dateTime": "2026-07-13T21:10:00+09:00"},
        "summary": "塾",
    }
    result = normalize_event("息子", raw)
    assert result == {
        "account_name": "息子",
        "summary": "塾",
        "start": datetime(2026, 7, 13, 18, 55, tzinfo=result["start"].tzinfo),
        "all_day": False,
    }


def test_normalize_event_all_day():
    raw = {
        "start": {"date": "2026-07-14"},
        "end": {"date": "2026-07-15"},
        "summary": "バイト　書類提出",
    }
    result = normalize_event("娘", raw)
    assert result == {
        "account_name": "娘",
        "summary": "バイト　書類提出",
        "start": datetime(2026, 7, 14),
        "all_day": True,
    }


def test_normalize_event_empty_title_becomes_yotei():
    raw = {"start": {"dateTime": "2026-07-13T09:00:00+09:00"}, "summary": ""}
    result = normalize_event("息子", raw)
    assert result["summary"] == "予定"


def test_fetch_events_success():
    accounts = {"息子": "calendar.example_son", "娘": "calendar.example_daughter"}

    def fake_get_events(entity_id, start, end):
        if entity_id == "calendar.example_son":
            return [{"start": {"dateTime": "2026-07-13T18:55:00+09:00"}, "summary": "塾"}]
        return []

    events, skipped = fetch_events(accounts, datetime(2026, 7, 13), datetime(2026, 7, 14), fake_get_events)
    assert skipped == []
    assert len(events) == 1
    assert events[0]["account_name"] == "息子"
    assert events[0]["summary"] == "塾"


def test_fetch_events_skips_failing_account_and_continues():
    accounts = {"息子": "calendar.example_son", "パパ": "calendar.example_father"}

    def fake_get_events(entity_id, start, end):
        if entity_id == "calendar.example_son":
            raise RuntimeError("entity not loaded")
        return [{"start": {"dateTime": "2026-07-13T20:00:00+09:00"}, "summary": "会議"}]

    events, skipped = fetch_events(accounts, datetime(2026, 7, 13), datetime(2026, 7, 14), fake_get_events)
    assert skipped == ["息子"]
    assert len(events) == 1
    assert events[0]["account_name"] == "パパ"


def test_fetch_events_all_accounts_fail():
    accounts = {"息子": "calendar.example_son", "パパ": "calendar.example_father"}

    def fake_get_events(entity_id, start, end):
        raise RuntimeError("auth expired")

    events, skipped = fetch_events(accounts, datetime(2026, 7, 13), datetime(2026, 7, 14), fake_get_events)
    assert events == []
    assert set(skipped) == {"息子", "パパ"}


def test_is_total_failure_true_when_all_skipped_and_no_events():
    assert is_total_failure({"息子", "パパ"}, ["息子", "パパ"], []) is True


def test_is_total_failure_false_when_partial_skip():
    assert is_total_failure({"息子", "パパ"}, ["息子"], [{"account_name": "パパ"}]) is False


def test_is_total_failure_false_when_no_skip():
    assert is_total_failure({"息子", "パパ"}, [], []) is False

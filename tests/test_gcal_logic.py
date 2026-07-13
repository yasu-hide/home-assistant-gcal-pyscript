from datetime import datetime
from pyscript.modules.gcal_logic import greeting, format_hhmm, format_announcement


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

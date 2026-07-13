# home-assistant-gcal-pyscript

Home Assistant上でGoogleカレンダーの予定を毎朝スマートスピーカーで読み上げるための実装です。

- `pyscript/modules/gcal_logic/` — HA/pyscriptランタイムに依存しない純粋ロジック(予定の整形・グルーピング・失敗通知文の組み立て)
- `pyscript/gcal_announcement.py` — 上記を使うHA連携アダプタ(`calendar.get_events`呼び出し、`persistent_notification`連携)
- `automations/gcal_announcement.yaml.example` — 平日/休日トリガーのAutomation定義例

## 前提条件

- Home Assistant(HACS導入済み)
- HACS経由の`pyscript`統合
- 読み上げ対象アカウント分のGoogle Calendar連携(Settings > Devices & Services から追加。共有カレンダーは1つのGoogleアカウントに集約しておくとOAuth設定が1回で済む)
- `workday`統合(平日/休日判定用。country: JPで日本の祝日に対応)
- 読み上げに使うTTSエンジンと`media_player`のentity(スピーカーの種類は問わない。HAが対応していればAlexa等でも動作するはず)

## デプロイ手順

1. HACSから`pyscript`統合を追加する(Settings > Devices & Services > 統合を追加)。
2. **Studio Code Server**または**File editor**アドオンを使い、このリポジトリの`pyscript/`ディレクトリの内容をそのまま`/config/pyscript/`にコピーする。
3. `automations/gcal_announcement.yaml.example`をコピーして`gcal_announcement.yaml`にリネームし、`accounts`配下を実際の「名前 → calendar entity_id」のマッピングに書き換える。対象のcalendar entity_idはDeveloper Tools > States で`calendar.`から始まるentityを検索すると確認できる。`tts.speak`先の`entity_id`(TTSエンジン)・`media_player_entity_id`(スピーカー)も自分の環境のものに書き換える。
4. File editor/Studio Code Serverで、作成した`gcal_announcement.yaml`を`/config/automations/`などに配置し、`configuration.yaml`の`automation:`セクションを`!include_dir_merge_list automations/`のようなsplit config形式にしておく(このファイルは`accounts`をYAMLアンカー/エイリアスで平日/休日の2つのautomation間で共有しているため、HAの「Edit in YAML」で1automationずつ個別に貼り付ける方法では取り込めない)。
5. Settings > System から再起動する、またはDeveloper Tools > YAML の「Automationのリロード」で設定を反映する。
6. 対象のAutomationをUIから手動トリガー(Automation詳細画面の「実行」ボタン)し、Google Calendar連携・`workday`統合・TTS/`media_player`が正しく動作することを確認する。

## テスト

pyscript本体に依存しない純粋ロジック(`pyscript/modules/gcal_logic/`)は、HA環境なしで`pytest`でテストできる。

```
pip install pytest
pytest
```

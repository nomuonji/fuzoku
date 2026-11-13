# 制作の流れ（工場）

1話＝`productions/<話数>/` の1フォルダ。台本から書き出しまで、ここに全部入る。

## 流れ

| # | やること | コマンド・置き場所 | 誰が止めるか |
| --- | --- | --- | --- |
| 1 | 場面を立てる | `docs/episode-ideas.md` の見本と同じ深さで新しく一つ。あるあるの一コマを一つだけ。使用済みに追記 | |
| 2 | 作業場所を作る | `python tools/new_episode.py 002 biyoushitsu` | |
| 3 | 生の声から型を学ぶ | 知恵袋・投稿サイト・アンケート記事 → `docs/research/voices/002-biyoushitsu.md` に型だけ | |
| 4 | 台本 | `productions/002/script.md`（`AGENTS.md` の作り方と構成表に従う） | **Yutoのチェック。OKが出るまで先に進まない**（毎日の予約実行だけは例外。下の「毎日の予約実行」の自己点検で代える） |
| 5 | ナレーション | `lines.json` に台詞を1行ずつ → `bash tools/voicevox/start.sh` → `python tools/vo.py productions/002` | |
| 6 | 画と秒数 | `build_timeline.py`（秒数・字幕・効果音のきっかけ）と `scene.py`（場面ごとの画）を書き換える。雛形は #001 のコード | |
| 7 | 書き出し | `python tools/make.py productions/002`（手元）か、Actions の **render** を手動実行 | 書き出した動画を自分で見る。コマ送りで字幕の折り返しと画の切れ目を確認 |
| 8 | 投稿する | **直接**：`python tools/youtube.py productions/002`（`--private` で非公開の確認投稿）か、Actions の **render** で「今すぐ投稿」。**予約**：`python tools/drive.py send productions/002` か render で「ちんすけの予約キューへ」。Driveの `v-stock/ちんすけ/queue` に動画と同名のJSON（タイトル・概要欄・ハッシュタグ）が入り、video-publisher が予定の時刻に投稿する | 送る前に `out/002-*.json` のタイトルと概要欄を見る |
| 8.5 | TikTok にも出す | YouTube に公開したら `python tools/tiktok.py productions/002 ../video-publisher`。動画を TikTok 用に詰め直して video-publisher の `incoming/fuzoku-<話数>-<日付>` ブランチに置き、Queue From Repo が Buffer 経由で TikTok（`chinsukedt`）に出す。episode.json に `tiktok.requested` が入る（二重に出さない）。結果は video-publisher の Queue From Repo のログで確かめる | 2026-11-07 Yuto指示 |
| 9 | 公開済みにする | Actions の **collect**（1日2回自動）が `posted` のJSONから YouTube ID を読み、`episode.json` を `published` にする。手元なら `python tools/drive.py collect` | |
| 10 | 受け皿に載せる | `python tools/sync_chonmage.py ../chonmage-ja` → chonmage-ja で build → push | |

一部だけ直すとき：
- 台詞を1行直した → `python tools/vo.py productions/002 7`（7行目だけ）→ `make.py`
- 音だけ直した → `python tools/make.py productions/002 --audio`（画は前回のまま、数十秒）

## 決まっている部品

| 部品 | 場所 |
| --- | --- |
| 男（A案、表情4種、正面・横・背面） | `assets/character/man/`。顔を直すときは `tools/character/man.py` → `python tools/character/build.py` |
| 通りすがりの女（裾と靴） | `assets/character/woman_pass.svg` |
| 風俗チラシ（静止画3枚） | `assets/flyers/` |
| BGM | `assets/bgm/signs-to-nowhere.mp3`（CC BY 4.0。クレジットは `make.py` が概要欄に入れる） |
| 声 | VOICEVOX 青山龍星「しっとり」（style 84）。設定は `episode.json` の `voice` |
| 環境音・効果音の追加候補／音の確認（任意） | Openverse（CC素材検索）と earshot（音の測定・コード製効果音）。[asset-sources.md](https://github.com/nomuonji/animation-factory/blob/main/docs/asset-sources.md)。注意は `AGENTS.md`「参照」 |
| 書き出し設定 | 1080×1920、30fps、H.264 crf25、音量 -14 LUFS |

## episode.json

| 項目 | 使い道 |
| --- | --- |
| `no` `slug` `title` | ファイル名と話の名前 |
| `status` | `draft` → `ready`（書き出し済み）→ `queued`（ちんすけのキューに入れた）→ `published` |
| `scene` `line` | chonmage-ja の `/souda/` に出る、場面の一文と言語化の一行 |
| `escape` | `/souda/` でその話の下に出す逃げ道（`yumeoto` か `delice`） |
| `still_time` | `/souda/` に載せる静止画を何秒目から切るか |
| `youtube` | タイトル・概要欄・ハッシュタグ。**「風俗」・リンク・店名・料金を入れない** |
| `variant` | 実験の条件（`experiment` `opening` `target_seconds`）。`opening:"direct"` で先出しから巻き戻し・カードなしで本編へ（`opening_card:false` は暗転だけ残す旧案）。`docs/experiments.md` |
| `youtube_id` `published` | 公開したら埋める。`/souda/` に動画が埋め込まれる |

## 投稿（video-publisher）

- 投稿先は `publish.json`（Driveの `v-stock` の下の `ちんすけ`）。投稿の時刻と、YouTube以外のSNSにも出すかどうかは、video-publisher 側の「ちんすけ」の設定（config.json）が決める
- 直接投稿（`tools/youtube.py`）は動画をDriveに置かない。ちんすけのチャンネルの認証（リフレッシュトークン）だけを config.json から読み、OAuthクライアントは secret の `GOOGLE_CLIENT_JSON`（video-publisher と同じクライアントのJSON）を使う
- Driveに手で入れても投稿される。そのときは同名のJSONを横に置かないと、ちんすけ共通のタイトル・概要欄で出る
- 認証は video-publisher と同じサービスアカウント。fuzoku の Actions には secret `GOOGLE_SERVICE_ACCOUNT_JSON` を入れておく
- `aiLabel`（`publish.json` の `ai_label`）は true。チラシに実写風のAI画像を使っているので、YouTubeの「改変・合成コンテンツ」の申告を付ける

## 公開と誘導

収益の受け皿は chonmage-ja（https://ja.chon-mage.com/souda/）。ユメオトとデリスの説明ページへはそこからつなぐ。

- **YouTube から外へは何もつながない。** 概要欄・固定コメント・チャンネルのリンク欄・動画内の文字・ナレーションのどれにも、chonmage-ja・ユメオト・デリスのURLや名前、「プロフから」などの誘導を入れない。YouTubeの規約は性的サービスへのリンクと口頭の誘導を禁じていて、外部リンク違反でチャンネルごと消された例がある
- つながりは **chonmage-ja → YouTube の一方向だけ**。`/souda/` が動画を埋め込み、シリーズ名で検索した人がそこにたどり着く
- チャンネル名・動画の締めは「くだらない世界」「そうだ、風俗行こう。」で揃え、検索されたときに `/souda/` が出るようにする

## 毎日の予約実行（2026-11-04 Yuto指示）

毎日夕方、スケジュールタスクが台本から公開まで1本作る。人のチェックが入らないので、次を守る。

- 書く前に `docs/research/advanced-capitalism-emptiness.md` を最後まで読む。場面は `docs/episode-ideas.md` の見本と同じ深さで**新しく立てる**（見本を順に消費しない。立て方は同ファイル）。使用済みと場面・切り口を重ねない。公開したら「使用済み」に場面・突く所・言語化を追記して commit する
- 台本は書いたあと `script.md` の末尾に自己点検を書く：AGENTS.md の「空虚さの芯」（突く所はどれか、資本主義が広告に使える言語化になっていないか、男も輪の中にいるか）、「台本の作り方」5項目、構成表、「やってはいけない」、「リアルにする工夫」を1項目ずつ照らし、満たしていない所は直してから進む
- 言語化の一行は、候補を3つ以上書いてから一番鋭いものを選ぶ。候補も `script.md` に残す。比喩・擬人化・反転の言葉遊びで解読が要る候補は落とす（2026-11-07）
- **聞き取りテスト（2026-11-07 Yuto指示、#004「poetic過ぎて何の話か分からない」を受けて）**：`script.md` に中学生向けの二文要約を書き、台詞だけで通じるか確かめる。最初の10秒で何の場面かを声で言い切る。説明は4〜6行の普通の話し言葉。尺は75〜90秒・台詞16〜22行（AGENTS.md「分かりやすさ」）。冒頭は検証E1の「直接入り」（先出しからそのまま本編へ、巻き戻し・カードなし。2026-11-13）。**書く前に `docs/experiments.md` を読み、公開48時間後の数字は `tools/metrics.py` で記録する**
- 書き出しは先に `QUALITY=draft` で通し、要所のコマを並べて目で確かめる（字幕の折り返し、画の切れ目、先出し・シリーズ名・チラシ・ネオン）
- **投稿は依頼ファイルの push で行う（2026-11-07 Yuto指示）。** Actions を直接起動せず、`productions/<話数>/post-request.json` に `{"post": "公開"}` を書いて main に commit・push する。`post-on-push` ワークフローが render を回して投稿し、episode.json に youtube_id を書き戻す。`"非公開"` `"書き出しだけ"` `"予約キュー"` も使える。youtube_id が入っている話は投稿されない。結果は Actions の post-on-push の実行ログ（「公開で投稿：」）で拾う
- **YouTube に公開できたら TikTok にも出す（2026-11-07 Yuto指示）。** fuzoku を pull して `python tools/tiktok.py productions/<話数> ../video-publisher`（video-publisher も push 権限でクローンしておく）。episode.json の変更（`tiktok`）を fuzoku の main に commit・push する。video-publisher の Queue From Repo の実行ログから「TikTok ちんすけ/… → Buffer …」を拾う。TikTok だけ失敗しても YouTube は出し直さない。理由を報告する
- 声・画・投稿のどこかで失敗したら、公開しない。直せなければ非公開で上げるか、何も上げずに報告する
- YouTube側に chonmage-ja・ユメオト・デリスの名前やリンクを絶対に出さない。タイトルとサムネに「風俗」を入れない

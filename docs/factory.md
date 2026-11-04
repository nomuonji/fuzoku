# 制作の流れ（工場）

1話＝`productions/<話数>/` の1フォルダ。台本から書き出しまで、ここに全部入る。

## 流れ

| # | やること | コマンド・置き場所 | 誰が止めるか |
| --- | --- | --- | --- |
| 1 | 場面を選ぶ | `docs/episode-ideas.md` から一つ。あるあるの一コマを一つだけ | |
| 2 | 作業場所を作る | `python tools/new_episode.py 002 biyoushitsu` | |
| 3 | 生の声から型を学ぶ | 知恵袋・投稿サイト・アンケート記事 → `docs/research/voices/002-biyoushitsu.md` に型だけ | |
| 4 | 台本 | `productions/002/script.md`（`AGENTS.md` の作り方と構成表に従う） | **Yutoのチェック。OKが出るまで先に進まない** |
| 5 | ナレーション | `lines.json` に台詞を1行ずつ → `bash tools/voicevox/start.sh` → `python tools/vo.py productions/002` | |
| 6 | 画と秒数 | `build_timeline.py`（秒数・字幕・効果音のきっかけ）と `scene.py`（場面ごとの画）を書き換える。雛形は #001 のコード | |
| 7 | 書き出し | `python tools/make.py productions/002`（手元）か、Actions の **render** を手動実行 | 書き出した動画を自分で見る。コマ送りで字幕の折り返しと画の切れ目を確認 |
| 8 | 投稿する | **直接**：`python tools/youtube.py productions/002`（`--private` で非公開の確認投稿）か、Actions の **render** で「今すぐ投稿」。**予約**：`python tools/drive.py send productions/002` か render で「ちんすけの予約キューへ」。Driveの `v-stock/ちんすけ/queue` に動画と同名のJSON（タイトル・概要欄・ハッシュタグ）が入り、video-publisher が予定の時刻に投稿する | 送る前に `out/002-*.json` のタイトルと概要欄を見る |
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
| `youtube_id` `published` | 公開したら埋める。`/souda/` に動画が埋め込まれる |

## 投稿（video-publisher）

- 投稿先は `publish.json`（Driveの `v-stock` の下の `ちんすけ`）。投稿の時刻と、YouTube以外のSNSにも出すかどうかは、video-publisher 側の「ちんすけ」の設定（config.json）が決める
- 直接投稿（`tools/youtube.py`）は動画をDriveに置かない。ちんすけのチャンネルの認証（リフレッシュトークン）だけを config.json から読み、OAuthクライアントは secret の `GOOGLE_CLIENT_ID`・`GOOGLE_CLIENT_SECRET`（video-publisher と同じ値）を使う
- Driveに手で入れても投稿される。そのときは同名のJSONを横に置かないと、ちんすけ共通のタイトル・概要欄で出る
- 認証は video-publisher と同じサービスアカウント。fuzoku の Actions には secret `GOOGLE_SERVICE_ACCOUNT_JSON` を入れておく
- `aiLabel`（`publish.json` の `ai_label`）は true。チラシに実写風のAI画像を使っているので、YouTubeの「改変・合成コンテンツ」の申告を付ける

## 公開と誘導

収益の受け皿は chonmage-ja（https://ja.chon-mage.com/souda/）。ユメオトとデリスの説明ページへはそこからつなぐ。

- **YouTube から外へは何もつながない。** 概要欄・固定コメント・チャンネルのリンク欄・動画内の文字・ナレーションのどれにも、chonmage-ja・ユメオト・デリスのURLや名前、「プロフから」などの誘導を入れない。YouTubeの規約は性的サービスへのリンクと口頭の誘導を禁じていて、外部リンク違反でチャンネルごと消された例がある
- つながりは **chonmage-ja → YouTube の一方向だけ**。`/souda/` が動画を埋め込み、シリーズ名で検索した人がそこにたどり着く
- チャンネル名・動画の締めは「くだらない世界」「そうだ、風俗行こう。」で揃え、検索されたときに `/souda/` が出るようにする

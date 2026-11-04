# くだらない世界 —「そうだ、風俗行こう。」

深夜のセルフレジ、美容室の会話、誕生日の通知。高度資本主義の空虚な一コマを、スケベそうな男がハードボイルドに一行で言い当て、通りすがりの女の残り香で「そうだ、風俗行こう。」へ流れる。50〜60秒のアニメーションShortsシリーズの制作工場。

**エージェントは `AGENTS.md` から読む。** 台本の作り方はそこが最優先。

## 1話を作る

```bash
python tools/new_episode.py 002 biyoushitsu     # 作業場所を作る
# script.md を書く → Yutoのチェック → lines.json
bash tools/voicevox/start.sh                     # VOICEVOXエンジン起動
python tools/vo.py productions/002               # ナレーション
# build_timeline.py と scene.py を場面に合わせて書き換える
python tools/make.py productions/002             # → out/002-biyoushitsu.mp4 と upload.txt
python tools/sync_chonmage.py ../chonmage-ja     # 受け皿ページに載せる
```

GitHub Actions の **render** を手動実行しても同じものが書き出せる（Artifactsに mp4・概要欄の文面・静止画）。詳しい流れと公開ルールは [`docs/factory.md`](docs/factory.md)。

## 中身

| 場所 | 中身 |
| --- | --- |
| `AGENTS.md` | 台本の作り方・構成・守ること（最優先） |
| `docs/factory.md` | 制作の流れ、episode.json、公開と誘導のルール |
| `docs/series-bible.md` | シリーズの決めごと、キャラ設定 |
| `docs/episode-ideas.md` | 場面の候補 |
| `docs/research/` | 空虚さの根拠（台詞には使わない）、`voices/` に生の声から学んだ型 |
| `productions/<話数>/` | 1話分の全部（台本、lines.json、episode.json、声、画と音のコード） |
| `productions/_template/` | 新しい話の雛形 |
| `assets/character/` | 男（A案）と通りすがりの女のSVG |
| `assets/flyers/` | 風俗チラシの静止画（白黒・文字なし） |
| `assets/bgm/` | BGMとクレジット |
| `tools/` | `new_episode.py` `vo.py` `make.py` `sync_chonmage.py`、`voicevox/`（エンジン起動）、`character/`（キャラ生成）、`cards/` |

## 誘導

受け皿は chonmage-ja の [/souda/](https://ja.chon-mage.com/souda/)。YouTube側からはどこにもつながない（規約で禁止）。chonmage-ja → YouTube の一方向だけ。

編集用の正本：[シリーズバイブル（Docs）](https://claude.ai/artifact/48pGCHSjeJ1USEsF6cbg7r) ／ [キャラクタービジュアルシート（Design）](https://claude.ai/artifact/S1e6i7eG6R16G9TBx2v6kt)

# #001 セルフレジ（v4・70秒）

命題：影の労働と自己搾取（イリイチ／ハン）。失われたものは「人にしてもらうこと」。オチは、セルフサービスの世界に残った最後の「フルサービス」。台本の考え方は [高度資本主義の虚無レポート](https://claude.ai/artifact/Qi1PwpCd5kj9Ffd3cnt1Z9)。

- 台本は `script_v4.md`（ナレーションは `lines.json`）。字幕・カット割り・効果音の秒数も同じファイル
- 声：VOICEVOX 青山龍星「しっとり」（style 84、速度0.92、ピッチ-0.04、抑揚0.85、オチだけ0.7）。`voicevox_tts.py` はエンジン（http://127.0.0.1:50021）が動いている前提

## 作り直し手順

1. VOICEVOXエンジンを起動 → `python voicevox_tts.py 84 0.92 -0.04 preview.mp3`（行ごとのwavも出る。`vo/` は加工済み）
2. `bgm.mp3` に [Signs To Nowhere](https://www.silvermansound.com/free-music/signs-to-nowhere) を置く（gitに入れない）
3. `python scene.py` → `python render_frames.py` → `python audio.py`
4. `ffmpeg -framerate 30 -i frames/%05d.jpg -i mix.wav -c:v libx264 -crf 25 -pix_fmt yuv420p -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -shortest out.mp4`

## 概要欄に必要なクレジット

```
Music: Signs To Nowhere by Shane Ivers - https://www.silvermansound.com
VOICEVOX:青山龍星
```

## 風俗チラシの写真

`assets/flyers/` の3枚（Yuto生成のAI画像を加工）。電柱に貼られたチラシとして、男が目を動かした直後に2.4秒だけ映す。白黒・暗転・粒子・雨染み。料金・店名・指名などの文字は切り落とし、文字の段はにじませて読めなくしてある。

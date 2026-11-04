# #001 セルフレジ（64秒）

台本は `script.md`、セリフは `lines.json`、各セリフの開始秒と字幕は `timeline.json`。

## 作り直し手順

1. 声：`python tts.py M2 Neutral`（Style-Bert-VITS2、JVNV M2。モデルはリポジトリ直下の `models/` に置く。gitには入れない）→ ffmpegで `rubberband=pitch=0.84` などをかけて `vo/` へ。いまの `vo/` は加工済み
2. BGM：`bgm/signs-to-nowhere.mp3` を [Silverman Sound](https://www.silvermansound.com/free-music/signs-to-nowhere) から落として置く（gitに入れない）
3. 画：`python scene.py` → `python render_frames.py`（1926枚、30fps）
4. 音：`python audio.py` → `mix.wav`（効果音はすべてコードで合成）
5. 書き出し：`ffmpeg -framerate 30 -i frames/%05d.jpg -i mix.wav -c:v libx264 -crf 25 -pix_fmt yuv420p -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -shortest out.mp4`

## 概要欄に必要なクレジット

```
Music: Signs To Nowhere by Shane Ivers - https://www.silvermansound.com
音声: Style-Bert-VITS2 JVNVコーパスモデル（jvnv-M2-jp, CC BY-SA 4.0）
```

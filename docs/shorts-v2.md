# V2 asset-first editing lab (experimental)
既存の tools/make.py、投稿契約、過去13話を保持。V2 は独立したローカル preview 経路。自動投稿しない。
## Production
1. docs/research/shorts-v2.md の市場・台本仮説を読み、動画ごとの視聴報酬と葛藤/回収を先に定義。
2. 台本と絵コンテを独立に設計。各ショットの目的を記録。素材（自作動画、AI生成素材、許諾素材、既存3Dレンダリング）を用意し、出典/権利をprovenanceに記録。レンダラーは権利を検証しない。
3. JSON manifestに秒数、素材、トリム、速度、画像のpush/pull、音響の時刻と音量、字幕を記述する。画面と台詞は1対1にしない。
4. python tools/v2/render.py path/to/manifest.json out/preview.mp4 --preview
5. 全編を音あり/なしで視聴。画が読めるか、効果が意味を持つか、台詞だけでも興味が続くか、オチに納得できるか確認。本人レビュー後に投稿経路の統合を判断。
## Manifest contract
{"shots":[{"src":"clip.mp4","kind":"video","seconds":2,"in":0.5,"speed":1.5,"provenance":"自作、制作日・権利"},{"src":"still.png","kind":"image","seconds":1,"motion":"push","provenance":"自作"}],"audio":[{"src":"voice.wav","at":0.2,"seconds":1.5,"gain":0.9,"provenance":"自作音声"}],"captions":[{"start":0.2,"end":1.7,"text":"字幕"}]}
- Python 3 + ffmpeg/ffprobe (libx264, libass); Noto Sans CJK JP推奨。外部API不要。
- 1080x1920/30fps、--preview 540x960。動画の音声は使わず別レイヤーとして指定する。素材が足りなければエラー、静止画への黙示フォールバックなし。最大60秒。
- 現段階はハードカット、素材速度、静止画カメラ、音声ミックス、字幕のMVP。多層映像合成/3D/AI素材生成/自動投稿は未実装。既存 animation-factory の tools/three/render3d.mjs, tools/render-production.mjs を素材供給候補として評価する。Remotion採用は必要性とライセンスを確認してから。
- 機能確認: python tools/v2/smoke.py (人工素材を使う統合スモーク、作品評価ではない)。

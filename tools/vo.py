"""lines.json -> vo/<n>.wav（VOICEVOX 青山龍星しっとり＋声の加工）

    python tools/vo.py productions/002            # 全行
    python tools/vo.py productions/002 3 7        # 3行目と7行目だけ作り直す

エンジンは tools/voicevox/start.sh で先に起動しておく。
声の設定は episode.json の "voice" で上書きできる（無ければ下の既定）。
"""
import json, pathlib, subprocess, sys, tempfile, urllib.parse, urllib.request

API = "http://127.0.0.1:50021"
DEFAULT = {"speaker": 84, "speed": 1.0, "pitch": -0.04, "intonation": 0.85, "volume": 1.0}
# 声の加工：低域を切る→軽く圧縮→ごく短い残響。ナレーションを部屋の中に置く
FX = "highpass=f=70,equalizer=f=220:t=q:w=1.2:g=2,equalizer=f=3200:t=q:w=1.5:g=-1.5," \
     "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,aecho=0.8:0.4:35:0.08"


def tts(text, v):
    q = json.load(urllib.request.urlopen(urllib.request.Request(
        f"{API}/audio_query?speaker={v['speaker']}&text=" + urllib.parse.quote(text), method="POST")))
    q.update(speedScale=v["speed"], pitchScale=v["pitch"], intonationScale=v["intonation"],
             volumeScale=v["volume"], prePhonemeLength=0.05, postPhonemeLength=0.1, outputSamplingRate=48000)
    return urllib.request.urlopen(urllib.request.Request(
        f"{API}/synthesis?speaker={v['speaker']}", data=json.dumps(q).encode(),
        headers={"Content-Type": "application/json"})).read()


def main():
    ep = pathlib.Path(sys.argv[1]).resolve()
    only = {int(x) for x in sys.argv[2:]}
    lines = json.loads((ep / "lines.json").read_text())
    meta = ep / "episode.json"
    v = dict(DEFAULT, **(json.loads(meta.read_text()).get("voice", {}) if meta.exists() else {}))
    (ep / "vo").mkdir(exist_ok=True)
    for i, text in enumerate(lines):
        if only and i not in only:
            continue
        with tempfile.NamedTemporaryFile(suffix=".wav") as raw:
            raw.write(tts(text, v)); raw.flush()
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw.name, "-af", FX, "-ar", "48000",
                            str(ep / f"vo/{i}.wav")], check=True)
        print(f"vo/{i}.wav  {text}")


if __name__ == "__main__":
    main()

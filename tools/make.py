"""1話をまとめて書き出す。

    python tools/make.py productions/001            # 画・音・書き出しまで
    python tools/make.py productions/001 --audio    # 音だけ作り直して書き出し直す（画は前回のまま）

順番：build_timeline.py → scene.py → 画（並列）→ audio.py → mp4
出力：out/<no>-<slug>.mp4、out/<no>-<slug>.json（video-publisher用のタイトル・概要欄）、
      out/<no>-<slug>.upload.txt（手で貼るとき用）、
      productions/<no>/still.jpg（chonmage-ja の /souda/ に載せる静止画）

vo/ が無い行があれば止まる。先に tools/vo.py で声を作る。
"""
import json, os, pathlib, shutil, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
BGM = ROOT / "assets/bgm/signs-to-nowhere.mp3"
CREDITS = "Music: Signs To Nowhere by Shane Ivers - https://www.silvermansound.com\nVOICEVOX:青山龍星"
FPS = 30


def run(*cmd, cwd):
    print("$", " ".join(map(str, cmd)), flush=True)
    subprocess.run([*map(str, cmd)], cwd=cwd, check=True)


def main():
    ep = pathlib.Path(sys.argv[1]).resolve()
    audio_only = "--audio" in sys.argv
    workers = int(os.environ.get("WORKERS", max(2, (os.cpu_count() or 2) * 2)))
    # QUALITY=draft は確認用（1080p・速い・粗い）。既定は公開用（1440p・crf16・slow）
    draft = os.environ.get("QUALITY") == "draft"
    env = dict(os.environ, SCALE="1" if draft else os.environ.get("SCALE", str(4 / 3)),
               JPEG_Q="90" if draft else os.environ.get("JPEG_Q", "95"))
    enc = ["-preset", "veryfast", "-crf", "25"] if draft else ["-preset", "slow", "-crf", "16"]
    meta = json.loads((ep / "episode.json").read_text())
    name = f"{meta['no']}-{meta['slug']}"
    lines = json.loads((ep / "lines.json").read_text())
    missing = [i for i in range(len(lines)) if not (ep / f"vo/{i}.wav").exists()]
    if missing:
        sys.exit(f"vo/ が足りない行: {missing}  →  python tools/vo.py {ep.relative_to(ROOT)}")
    if not (ep / "bgm.mp3").exists():
        shutil.copy(BGM, ep / "bgm.mp3")

    t0 = time.time()
    run(sys.executable, "build_timeline.py", cwd=ep)
    total = json.loads((ep / "timeline.json").read_text())["total"]
    n = int(total * FPS)
    if not audio_only:
        run(sys.executable, "scene.py", cwd=ep)
        frames = ep / "frames"
        frames.mkdir(exist_ok=True)
        for f in frames.glob("*.jpg"):
            f.unlink()
        step = -(-n // workers)
        procs = [subprocess.Popen([sys.executable, "render_frames.py", str(a), str(min(a + step, n))], cwd=ep, env=env)
                 for a in range(0, n, step)]
        if any(p.wait() for p in procs):
            sys.exit("render failed")
        print(f"frames {n} in {time.time() - t0:.0f}s", flush=True)
    run(sys.executable, "audio.py", cwd=ep)

    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    mp4 = out / f"{name}.mp4"
    run("ffmpeg", "-v", "error", "-y", "-framerate", FPS, "-i", "frames/%05d.jpg", "-i", "mix.wav",
        "-c:v", "libx264", *enc, "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-af", "loudnorm=I=-14:TP=-1.5", "-c:a", "aac", "-b:a", "192k", "-shortest", mp4, cwd=ep)

    st = meta.get("still_time")
    if st is not None:
        src = ep / f"frames/{int(st * FPS):05d}.jpg"
        run("ffmpeg", "-v", "error", "-y", "-i", src, "-vf", "scale=720:-1", "-q:v", "4", ep / "still.jpg", cwd=ep)

    yt = meta["youtube"]
    pub = json.loads((ROOT / "publish.json").read_text())
    # video-publisher が読むサイドカー。概要欄の末尾にハッシュタグは向こうが足す
    (out / f"{name}.json").write_text(json.dumps({
        "title": yt["title"],
        "description": f"{yt['description']}\n\n{CREDITS}",
        "hashtags": " ".join(yt.get("hashtags", [])),
        "aiLabel": pub.get("ai_label", True),
        "episode": meta["no"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / f"{name}.upload.txt").write_text(
        f"タイトル\n{yt['title']}\n\n概要欄\n{yt['description']}\n\n{' '.join(yt.get('hashtags', []))}\n\n{CREDITS}\n",
        encoding="utf-8")
    print(f"\n{mp4}  ({total:.1f}s, {time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()

"""公開した話を TikTok にも出す（Buffer 経由。video-publisher の Queue From Repo を使う）。2026-11-07 Yuto指示。

    python tools/tiktok.py productions/004 ../video-publisher            # 送る
    python tools/tiktok.py productions/004 ../video-publisher --dry-run  # 置くだけ（push しない）

流れ：
  1. 動画を用意する。out/<no>-<slug>.mp4 が無ければ、fuzoku の Actions（render / post-on-push）の
     成果物「<no>-<slug>」の最新を gh api で落とす
  2. TikTok 用に 1080x1920・最大 6Mbps に詰め直す（GitHub は 100MB を超えるファイルを push できない）
  3. video-publisher に incoming/fuzoku-<no> ブランチを切り、incoming/ちんすけ/<日付>-<no>-<slug>.mp4 と
     同名の .json（postNow: "TikTok"、tiktokAccount）を置いて push する
  4. video-publisher の Queue From Repo が Buffer に渡し、TikTok に投稿する（YouTube には出さない。
     YouTube は tools/youtube.py が fuzoku から直接、高画質で出している）
  5. episode.json に tiktok.requested を書く（同じ話を二重に出さないため）。結果は Queue From Repo の
     ログ「TikTok ちんすけ/… → Buffer shareNow → chinsukedt (post …)」で確かめる

TikTok アカウントは publish.json の tiktok_account（Buffer のチャンネル名。2026-11-07 時点 chinsukedt）。
キャプションはタイトル＋概要欄（BGMクレジット CC BY を含む）＋ハッシュタグ。#Shorts は外す。
YouTube と同じく、chonmage-ja・ユメオト・デリスの名前やリンク・誘導は入れない（概要欄にも無い）。
"""
import datetime, io, json, pathlib, subprocess, sys, zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = "nomuonji/fuzoku"
LIMIT = 95 * 1024 * 1024
BANNED = ("chonmage", "chon-mage", "ユメオト", "デリス", "yumeoto", "delice")


def run(*cmd, cwd=None):
    print("$", " ".join(map(str, cmd)), flush=True)
    return subprocess.run([*map(str, cmd)], cwd=cwd, check=True, capture_output=True, text=True).stdout


def fetch_artifact(name, dst):
    """fuzoku の Actions 成果物 <name> の最新から mp4 を取り出す。"""
    arts = json.loads(run("gh", "api", f"repos/{REPO}/actions/artifacts?name={name}&per_page=5"))["artifacts"]
    arts = [a for a in arts if not a.get("expired")]
    if not arts:
        sys.exit(f"成果物 {name} が無い。先に render を回す")
    raw = subprocess.run(["gh", "api", f"repos/{REPO}/actions/artifacts/{arts[0]['id']}/zip"], check=True, capture_output=True).stdout
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        member = next(m for m in z.namelist() if m.endswith(f"{name}.mp4"))
        dst.write_bytes(z.read(member))
    print(f"成果物 {arts[0]['id']}（{arts[0]['created_at']}）から {dst.name}")


def squeeze(src, dst):
    for rate in ("6M", "4M"):
        run("ffmpeg", "-v", "error", "-y", "-i", src, "-vf", "scale=1080:1920:flags=lanczos", "-c:v", "libx264",
            "-preset", "slow", "-crf", "18", "-maxrate", rate, "-bufsize", "12M", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", dst)
        if dst.stat().st_size < LIMIT:
            return
    sys.exit(f"{dst.name} が {dst.stat().st_size >> 20}MB。100MB 未満にならない")


def main():
    ep = pathlib.Path(sys.argv[1]).resolve()
    vp = pathlib.Path(sys.argv[2]).resolve()
    dry = "--dry-run" in sys.argv
    meta = json.loads((ep / "episode.json").read_text())
    if not meta.get("youtube_id"):
        sys.exit(f"#{meta['no']} は YouTube にまだ公開していない。TikTok は公開した話だけ")
    if (meta.get("tiktok") or {}).get("requested") and "--again" not in sys.argv:
        sys.exit(f"#{meta['no']} は TikTok に依頼済み（{meta['tiktok']['requested']}）。出し直すなら --again")
    pub = json.loads((ROOT / "publish.json").read_text())
    account = pub.get("tiktok_account") or sys.exit("publish.json に tiktok_account が無い")
    concept = pub.get("concept", "ちんすけ")
    name = f"{meta['no']}-{meta['slug']}"

    src = ROOT / f"out/{name}.mp4"
    if not src.exists():
        src.parent.mkdir(exist_ok=True)
        fetch_artifact(name, src)
    side = ROOT / f"out/{name}.json"
    post = json.loads(side.read_text()) if side.exists() else {
        "title": meta["youtube"]["title"], "description": meta["youtube"]["description"],
        "hashtags": " ".join(meta["youtube"].get("hashtags", [])), "aiLabel": pub.get("ai_label", True)}
    tags = " ".join(t for t in post.get("hashtags", "").split() if t.lower() != "#shorts")
    caption = f"{post['title']}\n\n{post['description']}"
    if any(b in caption for b in BANNED):
        sys.exit("キャプションに外への誘導・リンクが入っている。止める")

    day = datetime.date.today().isoformat()
    stem = f"{day}-{name}"
    branch = f"incoming/fuzoku-{meta['no']}-{day}"
    run("git", "fetch", "-q", "origin", "main", cwd=vp)
    run("git", "checkout", "-q", "-B", branch, "origin/main", cwd=vp)
    dst_dir = vp / "incoming" / concept
    dst_dir.mkdir(parents=True, exist_ok=True)
    squeeze(src, dst_dir / f"{stem}.mp4")
    (dst_dir / f"{stem}.json").write_text(json.dumps({
        "title": post["title"], "description": post["description"], "hashtags": tags,
        "aiLabel": bool(post.get("aiLabel", True)), "postNow": "TikTok", "tiktokAccount": account,
        "tiktokCaption": caption, "episode": meta["no"], "source": f"{REPO} productions/{meta['no']}",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"置いた: {dst_dir.relative_to(vp)}/{stem}.mp4（{(dst_dir / f'{stem}.mp4').stat().st_size >> 20}MB）と .json")
    if dry:
        print("--dry-run：push しない。video-publisher の作業ブランチは戻しておく")
        run("git", "checkout", "-q", "main", cwd=vp)
        run("git", "branch", "-q", "-D", branch, cwd=vp)
        for f in (dst_dir / f"{stem}.mp4", dst_dir / f"{stem}.json"):
            f.unlink(missing_ok=True)
        return
    run("git", "add", "incoming", cwd=vp)
    run("git", "commit", "-q", "-m", f"fuzoku #{meta['no']} → TikTok ({account})", cwd=vp)
    run("git", "push", "-q", "origin", branch, cwd=vp)
    run("git", "checkout", "-q", "main", cwd=vp)
    meta["tiktok"] = {"account": account, "requested": day, "branch": branch}
    (ep / "episode.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    print(f"TikTok に依頼：video-publisher {branch}（Queue From Repo が Buffer に渡す）")


if __name__ == "__main__":
    main()

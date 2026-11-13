"""YouTube Analytics API から、話ごとのインサイトを読んで metrics.json に記録する。

    python tools/analytics.py check            # 認証と権限（yt-analytics.readonly）が通るか確かめる
    python tools/analytics.py fetch 007        # 公開日から2日後までの数字を記録（窓 "api-d2"）
    python tools/analytics.py retention 007    # 維持率の曲線を表示（冒頭で何秒に落ちるか）
    python tools/analytics.py auto             # 公開から3日以上たち、まだ api-d2 が無い話を全部記録
    python tools/analytics.py video <YouTubeのID> <公開日YYYY-MM-DD> [--concept おもしろ] [--length 秒]
                                               # fuzoku の話でない動画（別チャンネルのコント等）の数字と維持率を表示する
    python tools/analytics.py check --concept おもしろ   # 別チャンネルの認証が通るか

認証は tools/youtube.py と同じ（Drive の config.json のリフレッシュトークン＋OAuthクライアント）。
ただし、トークンに yt-analytics.readonly の権限が付いている必要がある。
video-publisher のアプリの「YouTube認証」ボタンで認証し直すと付く（2026-11-13の変更）。

注意（2026-11-13時点で未検証。認証し直したあとの初回で確かめる）：
  - Analytics API の日付は太平洋時間の日単位。Studio の「48時間」とは一致しない。そのため窓の名前は "api-d2"
    （公開日〜2日後）にして、Studio の手入力（"48h"）とは別の窓として扱う。話どうしの比較は同じ窓どうしだけ
  - データには遅れがある。公開から3日たってから取る
  - 「視聴を続けた割合」に当たる指標が API にあるかは未確認。取れなければ維持率の曲線（retention）で代える
"""
import datetime, json, pathlib, sys

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import youtube as yt  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = ROOT / "productions"
WINDOW = "api-d2"


def concept_refresh_token(concept):
    """Drive の v-stock/<concept>/config.json のリフレッシュトークン。名前が完全一致しなければ前方一致で探す。"""
    import io
    from googleapiclient.http import MediaIoBaseDownload
    d = yt.gd.drive()
    root = yt.gd.child(d, None, yt.gd.CFG["drive_root"], folder=True) or sys.exit("v-stock が見つからない")
    fid = yt.gd.child(d, root, concept, folder=True)
    if not fid:
        q = f"'{root}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        names = d.files().list(q=q, fields="files(id,name)", pageSize=100, supportsAllDrives=True,
                               includeItemsFromAllDrives=True).execute()["files"]
        hit = [f for f in names if f["name"].startswith(concept)]
        if len(hit) != 1:
            sys.exit(f"コンセプト「{concept}」が決まらない（候補: {[f['name'] for f in names]}）")
        fid = hit[0]["id"]
    cfg = yt.gd.child(d, fid, "config.json") or sys.exit("config.json が無い")
    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, d.files().get_media(fileId=cfg, supportsAllDrives=True))
    while not dl.next_chunk()[1]:
        pass
    tok = (json.loads(buf.getvalue()).get("apiKeys") or {}).get("youtube_refresh_token")
    return tok or sys.exit(f"{concept} の config.json に youtube_refresh_token が無い")


def service(concept=None):
    cid, sec = yt.client_creds()
    token = concept_refresh_token(concept) if concept else yt.refresh_token()
    cred = Credentials(None, refresh_token=token, token_uri="https://oauth2.googleapis.com/token",
                       client_id=cid, client_secret=sec)
    return build("youtubeAnalytics", "v2", credentials=cred, cache_discovery=False)


def video_report(svc, vid, published, length=None):
    """fuzoku の話でない動画：公開日〜2日後（api-d2）と公開から今日まで、維持率の主な秒数を出す。記録はしない（呼び出し側が書く）。"""
    d0 = datetime.date.fromisoformat(published)
    out = {"video": vid, "published": published}
    for name, end in (("api-d2", d0 + datetime.timedelta(days=2)), ("since", datetime.date.today())):
        r = query(svc, vid, d0.isoformat(), end.isoformat(),
                  "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained")
        v, mins, avg, pct, subs = (r.get("rows") or [[0, 0, 0, 0, 0]])[0]
        row = {"views": int(v), "hours": round(mins / 60, 3), "avg_sec": round(avg, 1), "avgpct": round(pct, 1), "subs": int(subs)}
        try:
            t = query(svc, vid, d0.isoformat(), end.isoformat(), "views", dimensions="insightTrafficSourceType")
            row["feed"] = int(sum(x for k, x in (t.get("rows") or []) if k == "SHORTS"))
        except Exception:
            pass
        out[name] = row
    r = query(svc, vid, d0.isoformat(), datetime.date.today().isoformat(),
              "audienceWatchRatio", dimensions="elapsedVideoTimeRatio", sort="elapsedVideoTimeRatio")
    rows = r.get("rows", [])
    pts = {}
    for sec in (2, 3, 5, 8, 10, 15, 20, 30, 45):
        if length and sec > length:
            continue
        if not length:
            break
        c = [w for ratio, w in rows if ratio * length <= sec]
        pts[f"{sec}s"] = round(c[-1], 2) if c else None
    if rows:
        pts["end"] = round(rows[-1][1], 2)
    out["retention"] = pts if length else {"note": "--length が無いので秒に直せない", "end": pts.get("end")}
    print(json.dumps(out, ensure_ascii=False))
    for ratio, w in rows:
        if length:
            print(f"{ratio * length:5.1f}s {'#' * int(w * 40)} {w:.2f}")


def query(svc, vid, start, end, metrics, dimensions=None, sort=None):
    kw = dict(ids="channel==MINE", startDate=start, endDate=end, metrics=metrics, filters=f"video=={vid}")
    if dimensions:
        kw["dimensions"] = dimensions
    if sort:
        kw["sort"] = sort
    return svc.reports().query(**kw).execute()


def episode(no):
    meta = json.loads((P / no / "episode.json").read_text())
    if not meta.get("youtube_id") or not meta.get("published"):
        sys.exit(f"#{no} は公開前（youtube_id / published が無い）")
    return meta


def fetch(svc, no):
    meta = episode(no)
    d0 = datetime.date.fromisoformat(meta["published"])
    start, end = d0.isoformat(), (d0 + datetime.timedelta(days=2)).isoformat()
    vid = meta["youtube_id"]
    r = query(svc, vid, start, end, "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained")
    row = (r.get("rows") or [[0, 0, 0, 0, 0]])[0]
    views, minutes, avg_sec, avg_pct, subs = row
    feed = None
    try:
        t = query(svc, vid, start, end, "views", dimensions="insightTrafficSourceType")
        feed = sum(v for k, v in (t.get("rows") or []) if k == "SHORTS")
    except Exception as e:  # 流入元が取れなくても、他の数字は記録する
        print(f"流入元は取れなかった（{e}）")
    rec = {"window": WINDOW, "views": int(views), "hours": round(minutes / 60, 3), "avg_sec": round(avg_sec, 1),
           "avgpct": round(avg_pct, 1), "subs": int(subs), "recorded": datetime.date.today().isoformat(),
           "note": f"Analytics API。{start}〜{end}（太平洋時間の日単位）"}
    if feed is not None:
        rec["feed"] = int(feed)
    f = P / no / "metrics.json"
    data = json.loads(f.read_text()) if f.exists() else []
    data = [m for m in data if m.get("window") != WINDOW] + [rec]  # 同じ窓は上書き（再取得で値が確定していくため）
    f.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    print(f"#{no}: {rec}")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    args = sys.argv[2:]
    concept = None
    length = None
    if "--concept" in args:
        i = args.index("--concept"); concept = args[i + 1]; del args[i:i + 2]
    if "--length" in args:
        i = args.index("--length"); length = float(args[i + 1]); del args[i:i + 2]
    sys.argv = sys.argv[:2] + args
    svc = service(concept)
    if cmd == "video" and len(args) >= 2:
        video_report(svc, args[0], args[1], length)
        return
    if cmd == "check":
        r = svc.reports().query(ids="channel==MINE", startDate=(datetime.date.today() - datetime.timedelta(days=7)).isoformat(),
                                endDate=datetime.date.today().isoformat(), metrics="views").execute()
        print("OK: Analytics API に届いた。直近7日の視聴:", (r.get("rows") or [[0]])[0][0])
    elif cmd == "fetch" and len(sys.argv) > 2:
        fetch(svc, sys.argv[2])
    elif cmd == "retention" and len(sys.argv) > 2:
        meta = episode(sys.argv[2])
        d0 = datetime.date.fromisoformat(meta["published"])
        r = query(svc, meta["youtube_id"], d0.isoformat(), datetime.date.today().isoformat(),
                  "audienceWatchRatio", dimensions="elapsedVideoTimeRatio", sort="elapsedVideoTimeRatio")
        tl = json.loads((P / sys.argv[2] / "timeline.json").read_text()) if (P / sys.argv[2] / "timeline.json").exists() else {}
        length = tl.get("total")
        for ratio, watch in r.get("rows", []):
            sec = f"{ratio * length:5.1f}秒" if length else f"{ratio:.2f}"
            print(f"{sec}  {'#' * int(watch * 40)} {watch:.2f}")
    elif cmd == "auto":
        today = datetime.date.today()
        for d in sorted(p.name for p in P.iterdir() if p.name.isdigit()):
            m = json.loads((P / d / "episode.json").read_text())
            if not (m.get("youtube_id") and m.get("published")):
                continue
            if (today - datetime.date.fromisoformat(m["published"])).days < 3:
                continue
            f = P / d / "metrics.json"
            if f.exists() and any(x.get("window") == WINDOW for x in json.loads(f.read_text())):
                continue
            fetch(svc, d)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()

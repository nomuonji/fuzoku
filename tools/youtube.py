"""Driveを通さず、書き出した動画を「ちんすけ」のYouTubeチャンネルへ直接投稿する。

    python tools/youtube.py productions/001            # 公開で投稿
    python tools/youtube.py productions/001 --private  # 非公開で投稿（確認用）

チャンネルの認証は video-publisher と共用：
  - リフレッシュトークン … Driveの v-stock/ちんすけ/config.json の apiKeys.youtube_refresh_token
    （サービスアカウント GOOGLE_SERVICE_ACCOUNT_JSON で読むだけ。動画はDriveに置かない）
  - OAuthクライアント … 環境変数 GOOGLE_CLIENT_JSON（GCPのクライアントJSONそのまま）か GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET
    （video-publisher の同名secretと同じ値。トークンを発行したクライアントでないと更新できない）
タイトル・概要欄は out/<no>-<slug>.json（make.py が作るもの）を使う。
投稿したら episode.json に youtube_id・published を書き、status を published にする。
"""
import json, os, pathlib, sys, io

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import drive as gd  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent


def refresh_token():
    d = gd.drive()
    root = gd.child(d, None, gd.CFG["drive_root"], folder=True) or sys.exit("v-stock が見つからない")
    concept = gd.child(d, root, gd.CFG["concept"], folder=True) or sys.exit(f"{gd.CFG['concept']} が見つからない")
    cfg_id = gd.child(d, concept, "config.json") or sys.exit("config.json が無い")
    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, d.files().get_media(fileId=cfg_id, supportsAllDrives=True))
    while not dl.next_chunk()[1]:
        pass
    tok = (json.loads(buf.getvalue()).get("apiKeys") or {}).get("youtube_refresh_token")
    return tok or sys.exit(f"{gd.CFG['concept']} の config.json に youtube_refresh_token が無い（video-publisherでYouTube連携を先に）")


def client_creds():
    cid, sec = os.environ.get("GOOGLE_CLIENT_ID"), os.environ.get("GOOGLE_CLIENT_SECRET")
    if cid and sec:
        return cid, sec
    # GCPのOAuthクライアントJSON（{"web": {...}} / {"installed": {...}}）をそのまま入れてもよい
    raw = os.environ.get("GOOGLE_CLIENT_JSON") or os.environ.get("GOOGLE_OAUTH_CLIENT_JSON")
    if raw:
        j = json.loads(raw)
        j = j.get("web") or j.get("installed") or j
        return j["client_id"], j["client_secret"]
    sys.exit("GOOGLE_CLIENT_JSON（または GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET）が無い")


def main():
    ep = pathlib.Path(sys.argv[1]).resolve()
    private = "--private" in sys.argv
    meta = json.loads((ep / "episode.json").read_text())
    name = f"{meta['no']}-{meta['slug']}"
    mp4, side = ROOT / f"out/{name}.mp4", ROOT / f"out/{name}.json"
    if not mp4.exists() or not side.exists():
        sys.exit(f"out/{name}.mp4 / .json が無い。先に tools/make.py")
    if meta.get("youtube_id") and "--again" not in sys.argv:
        sys.exit(f"#{meta['no']} は投稿済み（{meta['youtube_id']}）。出し直すなら --again")
    post = json.loads(side.read_text())

    cid, sec = client_creds()
    cred = Credentials(None, refresh_token=refresh_token(), token_uri="https://oauth2.googleapis.com/token",
                       client_id=cid, client_secret=sec)
    yt = build("youtube", "v3", credentials=cred, cache_discovery=False)
    tags = [t.lstrip("#") for t in post.get("hashtags", "").split() if t.startswith("#")]
    body = {
        "snippet": {"title": post["title"], "description": f"{post['description']}\n\n{post.get('hashtags', '')}".strip(),
                    "tags": tags, "categoryId": "1", "defaultLanguage": "ja"},
        "status": {"privacyStatus": "private" if private else "public", "selfDeclaredMadeForKids": False,
                   "containsSyntheticMedia": bool(post.get("aiLabel", True))},
    }
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(mp4), mimetype="video/mp4", resumable=True, chunksize=8 << 20))
    res = None
    while res is None:
        st, res = req.next_chunk()
        if st:
            print(f"upload {int(st.progress() * 100)}%", flush=True)
    vid = res["id"]
    if not private:
        meta.update(youtube_id=vid, published=res.get("snippet", {}).get("publishedAt", "")[:10], status="published")
        (ep / "episode.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    ch = res.get("snippet", {}).get("channelTitle", "")
    print(f"{'非公開' if private else '公開'}で投稿：https://youtube.com/shorts/{vid}  （チャンネル：{ch}）")


if __name__ == "__main__":
    main()

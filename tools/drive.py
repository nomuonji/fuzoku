"""video-publisher（Driveの v-stock/<コンセプト>/queue）へ動画を渡す・投稿結果を読み戻す。

    python tools/drive.py send productions/001     # out/<no>-<slug>.mp4 と同名の .json を queue に入れる
    python tools/drive.py collect                  # posted の .json から youtubeId を episode.json に書き戻す

認証は環境変数 GOOGLE_SERVICE_ACCOUNT_JSON（video-publisher と同じサービスアカウント）。
投稿先は publish.json（drive_root と concept）。投稿の時刻は video-publisher 側の
コンセプト設定（config.json の postingTimes）が決める。こちらは queue に入れるだけ。

同名のJSON（サイドカー）に title / description / hashtags / aiLabel を入れておくと、
video-publisher がそれを使って投稿し、投稿後に posted へ移して youtubeId を書き足す。
"""
import io, json, os, pathlib, sys

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaInMemoryUpload

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "publish.json").read_text())


def drive():
    info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    cred = service_account.Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/drive"])
    return build("drive", "v3", credentials=cred, cache_discovery=False)


def child(d, parent, name, folder=None):
    q = f"name='{name}' and trashed=false"
    q += f" and '{parent}' in parents" if parent else ""
    if folder:
        q += " and mimeType='application/vnd.google-apps.folder'"
    r = d.files().list(q=q, fields="files(id,name)", pageSize=10, supportsAllDrives=True,
                       includeItemsFromAllDrives=True).execute()["files"]
    return r[0]["id"] if r else None


def concept_folders(d):
    root = child(d, None, CFG["drive_root"], folder=True) or sys.exit(f"Drive に {CFG['drive_root']} が見つからない")
    concept = child(d, root, CFG["concept"], folder=True) or sys.exit(f"{CFG['drive_root']}/{CFG['concept']} が見つからない")
    queue = child(d, concept, "queue", folder=True) or sys.exit("queue フォルダが無い")
    posted = child(d, concept, "posted", folder=True) or sys.exit("posted フォルダが無い")
    return queue, posted


def put(d, folder, name, media):
    old = child(d, folder, name)
    if old:  # 同じ名前があれば中身だけ差し替える（キューに二重に入れない）
        d.files().update(fileId=old, media_body=media, supportsAllDrives=True).execute()
        return old, "updated"
    f = d.files().create(body={"name": name, "parents": [folder]}, media_body=media, fields="id",
                         supportsAllDrives=True).execute()
    return f["id"], "created"


def send(ep_dir):
    ep = pathlib.Path(ep_dir).resolve()
    meta = json.loads((ep / "episode.json").read_text())
    name = f"{meta['no']}-{meta['slug']}"
    mp4, side = ROOT / f"out/{name}.mp4", ROOT / f"out/{name}.json"
    if not mp4.exists() or not side.exists():
        sys.exit(f"out/{name}.mp4 / .json が無い。先に tools/make.py")
    d = drive()
    queue, posted = concept_folders(d)
    if child(d, posted, mp4.name):
        sys.exit(f"{mp4.name} はもう posted にある（投稿済み）。出し直すなら slug を変える")
    # 先にJSON、次に動画。動画だけ先に見つかってJSON無しで投稿されるのを避ける
    _, s1 = put(d, queue, side.name, MediaInMemoryUpload(side.read_bytes(), mimetype="application/json"))
    _, s2 = put(d, queue, mp4.name, MediaFileUpload(str(mp4), mimetype="video/mp4", resumable=True))
    meta["status"] = "queued"
    (ep / "episode.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    print(f"{CFG['drive_root']}/{CFG['concept']}/queue ← {side.name} ({s1}), {mp4.name} ({s2})")


def collect():
    d = drive()
    _, posted = concept_folders(d)
    changed = 0
    for m in sorted(ROOT.glob("productions/[0-9]*/episode.json")):
        meta = json.loads(m.read_text())
        if meta.get("youtube_id"):
            continue
        fid = child(d, posted, f"{meta['no']}-{meta['slug']}.json")
        if not fid:
            continue
        buf = io.BytesIO()
        dl = MediaIoBaseDownload(buf, d.files().get_media(fileId=fid, supportsAllDrives=True))
        while not dl.next_chunk()[1]:
            pass
        rec = json.loads(buf.getvalue())
        if not rec.get("youtubeId"):
            continue
        meta.update(youtube_id=rec["youtubeId"], published=rec.get("postedAt", "")[:10], status="published")
        m.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
        changed += 1
        print(f"#{meta['no']} → https://youtube.com/shorts/{rec['youtubeId']}")
    print(f"{changed}話を公開済みにした")


if __name__ == "__main__":
    {"send": lambda: send(sys.argv[2]), "collect": collect}[sys.argv[1]]()

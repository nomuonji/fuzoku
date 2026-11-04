import json, urllib.request, os, sys, tarfile
repo="voicevox/voicevox_engine"; tag=sys.argv[1] if len(sys.argv)>1 else "cpu-latest"
tok=""
def get(url,accept):
    r=urllib.request.Request(url,headers={"Accept":accept}); return urllib.request.urlopen(r)
acc="application/vnd.oci.image.index.v1+json,application/vnd.docker.distribution.manifest.list.v2+json,application/vnd.docker.distribution.manifest.v2+json,application/vnd.oci.image.manifest.v1+json"
m=json.load(get(f"https://mirror.gcr.io/v2/{repo}/manifests/{tag}",acc))
if "manifests" in m:
    d=[x for x in m["manifests"] if x.get("platform",{}).get("architecture")=="amd64"][0]["digest"]
    m=json.load(get(f"https://mirror.gcr.io/v2/{repo}/manifests/{d}",acc))
cfg=json.load(get(f"https://mirror.gcr.io/v2/{repo}/blobs/{m['config']['digest']}","*/*"))
print(json.dumps(cfg.get("config",{}),indent=0)[:1500])
os.makedirs("root",exist_ok=True)
for i,l in enumerate(m["layers"]):
    print("layer",i,l["size"],flush=True)
    fn=f"layer{i}.tgz"
    with get(f"https://mirror.gcr.io/v2/{repo}/blobs/{l['digest']}","*/*") as r, open(fn,"wb") as f:
        while True:
            b=r.read(1<<20)
            if not b: break
            f.write(b)
    try:
        with tarfile.open(fn) as t: t.extractall("root",filter="fully_trusted")
    except Exception as e: print("extract err",e)
    os.remove(fn)
print("done")

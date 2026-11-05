#!/usr/bin/env bash
# VOICEVOXエンジンを http://127.0.0.1:50021 で起動する。
#   - docker があれば公式イメージを使う（GitHub Actions はこちら）
#   - 無ければ mirror.gcr.io からイメージの中身だけ取り出して直接起動する
#     （Docker Hub が 429 を返す環境向け。取り出し先は $VV_DIR、既定 ~/.voicevox）
set -euo pipefail
PORT=50021
HERE="$(dirname "$(readlink -f "$0")")"
if curl -sf "http://127.0.0.1:$PORT/version" >/dev/null; then echo "already running"; exit 0; fi

if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  docker run -d --rm --name voicevox -p 127.0.0.1:$PORT:50021 voicevox/voicevox_engine:cpu-latest >/dev/null
else
  VV_DIR="${VV_DIR:-$HOME/.voicevox}"
  ENGINE="$VV_DIR/root/opt/voicevox_engine"
  if [ ! -x "$ENGINE/run" ]; then
    mkdir -p "$VV_DIR" && (cd "$VV_DIR" && python3 "$HERE/pull.py" cpu-latest)
  fi
  (cd "$ENGINE" && nohup ./run --host 127.0.0.1 --port $PORT > "$VV_DIR/engine.log" 2>&1 &)
fi

for i in $(seq 1 90); do
  if curl -sf "http://127.0.0.1:$PORT/version" >/dev/null; then echo "voicevox $(curl -s http://127.0.0.1:$PORT/version)"; exit 0; fi
  sleep 2
done
echo "voicevox did not start" >&2; exit 1

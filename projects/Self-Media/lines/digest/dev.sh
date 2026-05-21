#!/bin/bash
# Dev preview — 改完 daily.html.j2 跑这个一行命令就看新效果
#
# Usage:
#   ./lines/digest/dev.sh [YYYY-MM-DD]              只 render HTML 看预览
#   ./lines/digest/dev.sh [YYYY-MM-DD] --shoot      额外跑 chrome 截 9 张 PNG
#
# Output structure (每日发布包):
#   daily/<date>/digest/publish/daily.html              浏览器预览
#   daily/<date>/digest/publish/images/*.png            9 张发布素材 (--shoot)
#   daily/<date>/digest/publish/post.md                 小红书文案

set -e
DATE="${1:-2026-05-12}"
SHOOT="${2:-}"
PORT="8765"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SAMPLE="$ROOT/lines/digest/fixtures/sample_enriched.json"
OUT_REL="daily/$DATE/digest/publish/daily.html"
OUT="$ROOT/$OUT_REL"
IMG_DIR="$ROOT/daily/$DATE/digest/publish/images"

# 1) Render Jinja2 → HTML
cd "$ROOT/pipeline" && python3 render_html.py "$SAMPLE" "$OUT"

# 2) HTTP server 守护（项目根作为 docroot）
if ! lsof -ti:$PORT > /dev/null 2>&1; then
  cd "$ROOT" && nohup python3 -m http.server $PORT > /tmp/self-media-server.log 2>&1 &
  sleep 0.5
  echo "✓ Server started on port $PORT"
else
  echo "✓ Server already on port $PORT"
fi

echo ""
echo "  → http://localhost:$PORT/$OUT_REL                  (9 张连看)"
echo "  → http://localhost:$PORT/$OUT_REL#cover            (单张封面)"
echo "  → http://localhost:$PORT/$OUT_REL#event-01         (单张事件 1)"
echo ""

# 3) 可选：跑 chrome headless 截 9 张 PNG
if [ "$SHOOT" = "--shoot" ]; then
  echo "→ Shooting 9 PNGs (chrome headless, ~30s) ..."
  cd "$ROOT/pipeline" && python3 screenshot.py "$SAMPLE" "$OUT" "$IMG_DIR"
  echo ""
  echo "  → $IMG_DIR/01-cover.png .. 09-event-08.png"
fi

"""
Headless Chrome → 9 PNGs (or N PNGs for N-1 events + 1 cover).

Reads enriched JSON to know how many events to capture. Serves the HTML via a
short-lived HTTP server (needed because chrome --headless follows :target via
URL fragments, which only work over http(s), not file://).

Usage:
    python pipeline/screenshot.py <enriched.json> <daily.html> <output_dir>

Output: <output_dir>/01-cover.png + 02-event-01.png ... NN-event-NN.png
"""
import http.server
import json
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path

from schemas.enriched import Daily


def serve(directory: Path, port: int = 0) -> tuple[socketserver.TCPServer, int]:
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(
        *a, directory=str(directory), **kw
    )
    server = socketserver.TCPServer(("127.0.0.1", port), handler)
    actual_port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, actual_port


def screenshot_slide(url: str, output: Path) -> None:
    # chrome --headless=new + --window-size=1080,1440 actually renders viewport
    # ~1400px (subtracts ~40px for chrome chrome). To get a true 1080×1440 image
    # that includes the footer (bottom-anchored absolute element), shoot at
    # 1080×1500 and then crop top 1440 in Python.
    tmp_full = output.with_suffix(".raw.png")
    subprocess.run(
        [
            "google-chrome",
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            "--window-size=1080,1560",
            # web font CDN — without this the LXGW WenKai / Noto Serif fonts
            # don't arrive in time and chrome falls back to thin generic faces
            "--virtual-time-budget=15000",
            "--run-all-compositor-stages-before-draw",
            f"--screenshot={tmp_full}",
            url,
        ],
        check=True,
        capture_output=True,
    )
    from PIL import Image
    img = Image.open(tmp_full)
    img.crop((0, 0, 1080, 1440)).save(output)
    tmp_full.unlink()


def main(enriched_path: Path, html_path: Path, output_dir: Path) -> None:
    data = json.loads(enriched_path.read_text(encoding="utf-8"))
    daily = Daily.model_validate(data)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Serve the directory containing the html file
    served_dir = html_path.parent
    server, port = serve(served_dir)
    try:
        base = f"http://127.0.0.1:{port}/{html_path.name}"
        time.sleep(0.3)  # give server a beat to come up

        slides = ["cover"] + [e.id for e in daily.events]
        for idx, slide in enumerate(slides, start=1):
            url = f"{base}#{slide}"
            out = output_dir / f"{idx:02d}-{slide}.png"
            screenshot_slide(url, out)
            print(f"  ✓ {out.name}")
        print(f"✓ {len(slides)} PNG → {output_dir}")
    finally:
        server.shutdown()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))

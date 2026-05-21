"""
Render daily HTML from enriched JSON via Jinja2.

Usage:
    python pipeline/render_html.py <enriched.json> <output.html>

Example:
    python pipeline/render_html.py fixtures/sample_enriched.json /tmp/daily.html
"""
import json
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from schemas.enriched import Daily


def render(enriched_path: Path, output_path: Path) -> None:
    data = json.loads(enriched_path.read_text(encoding="utf-8"))
    daily = Daily.model_validate(data)

    templates_dir = Path(__file__).parent / "templates"
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=False,            # we explicitly use |safe; pre-escaped HTML in stories
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("daily.html.j2")
    html = template.render(daily=daily)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"✓ Rendered {daily.total_events()} events → {output_path} ({len(html):,} bytes)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    render(Path(sys.argv[1]), Path(sys.argv[2]))

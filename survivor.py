import argparse
import html
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_DIR / "survivor_files"
STORAGE_DIR = Path("./storage") if Path("./storage").exists() else PROJECT_DIR / "storage"
STATE_FILE = STORAGE_DIR / "site_state.json"

NAME_MAP = {
    "Charlie": "Charlie",
    "Stephenie K": "Stephenie",
    "Q": "Q",
    "Dee": "Dee",
    "Coach": "Coach",
    "Rick": "Rick",
    "Jenna": "Jenna",
    "Christian": "Christian",
    "Cirie": "Cirie",
    "Kyle": "Kyle",
    "Jonathan": "Jonathan",
    "Aubry": "Aubry",
    "Angelina": "Angelina",
    "Savannah": "Savannah",
    "Chrissy": "Chrissy",
    "Mike": "mike",
    "Colby Donaldson": "Colby",
    "Kamila": "Kamilla",
    "Rizo": "Rizo",
    "Geneieve": "Genevieve",
    "Ozzy": "Ozzy",
    "Joe": "Joe",
    "Tiffany": "Tiffany",
    "Emily": "Emily",
}

GROUPS = {
    "Seagrens": [
        "Charlie",
        "Stephenie K",
        "Q",
        "Dee",
        "Coach",
        "Rick",
        "Jenna",
        "Christian",
    ],
    "Youngs": [
        "Cirie",
        "Kyle",
        "Jonathan",
        "Aubry",
        "Angelina",
        "Savannah",
        "Chrissy",
        "Mike",
    ],
    "Smiths": [
        "Colby Donaldson",
        "Kamila",
        "Rizo",
        "Geneieve",
        "Ozzy",
        "Joe",
        "Tiffany",
        "Emily",
    ],
}

TEAM_COLORS = {
    "Seagrens": "#e27648",
    "Youngs": "#60a7a1",
    "Smiths": "#6fc1d9",
}

TEAM_NAME_STYLES = {
    "Seagrens": {"border": "#894b74", "fill": "#e1b14b"},
    "Youngs": {"border": "#cfb664", "fill": "#38764d"},
    "Smiths": {"border": "#c6e89c", "fill": "#e2719c"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Survivor static website as index.html."
    )
    parser.add_argument(
        "--output",
        default="index.html",
        help="Output HTML file path. Default: index.html",
    )
    parser.add_argument(
        "--title",
        default="Survivor 50 Fantasy League",
        help="Page title shown in the browser and header.",
    )
    parser.add_argument(
        "--eliminated",
        nargs="*",
        default=None,
        help="Set the eliminated players list for this run.",
    )
    parser.add_argument(
        "--clear-eliminated",
        action="store_true",
        help="Clear all eliminated players before generating the site.",
    )
    parser.add_argument(
        "--save-state",
        action="store_true",
        help="Save the eliminated list to site_state.json for future runs.",
    )
    return parser.parse_args()


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"eliminated": []}

    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"eliminated": []}


def save_state(eliminated_names: list[str]) -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    if not STATE_FILE.exists():
        STATE_FILE.touch()

    STATE_FILE.write_text(
        json.dumps({"eliminated": eliminated_names}, indent=2),
        encoding="utf-8",
    )


def find_img(keyword: str, files: list[Path]) -> str | None:
    keyword_lower = keyword.lower()
    for file_path in files:
        if keyword_lower in file_path.name.lower():
            return f"{ASSETS_DIR.name}/{file_path.name}"
    return None


def collect_image_paths() -> dict[str, str | None]:
    files = [path for path in ASSETS_DIR.iterdir() if path.is_file()] if ASSETS_DIR.exists() else []
    return {name: find_img(keyword, files) for name, keyword in NAME_MAP.items()}


def css_text_shadow(border_color: str) -> str:
    offsets = [
        (-3, 0),
        (3, 0),
        (0, -3),
        (0, 3),
        (-2, -2),
        (-2, 2),
        (2, -2),
        (2, 2),
    ]
    return ", ".join(f"{dx}px {dy}px 0 {border_color}" for dx, dy in offsets)


def render_card(name: str, image_path: str | None, is_eliminated: bool) -> str:
    safe_name = html.escape(name)
    image_html = (
        f'<img src="{html.escape(image_path)}" alt="{safe_name}">' if image_path
        else '<div class="missing-image">No image found</div>'
    )
    eliminated_class = " eliminated" if is_eliminated else ""

    return f"""
        <article class="card{eliminated_class}">
          <div class="image-wrap">
            {image_html}
            {"<div class='stamp'>ELIMINATED</div>" if is_eliminated else ""}
          </div>
          <div class="name">{safe_name}</div>
        </article>
    """


def render_group(
        group_name: str,
        names: list[str],
        image_paths: dict[str, str | None],
        eliminated: set[str],
) -> str:
    style = TEAM_NAME_STYLES[group_name]
    team_shadow = css_text_shadow(style["border"])
    cards_html = "\n".join(
        render_card(name, image_paths.get(name), name in eliminated)
        for name in names
    )

    return f"""
      <section class="tribe" style="--tribe-bg: {TEAM_COLORS[group_name]};">
        <h2 class="tribe-title" style="color: {style["fill"]}; text-shadow: {team_shadow};">
          {html.escape(group_name)}
        </h2>
        <div class="card-grid">
          {cards_html}
        </div>
      </section>
    """


def build_html(title: str, eliminated_names: list[str]) -> str:
    image_paths = collect_image_paths()
    eliminated_set = set(eliminated_names)

    sections_html = "\n".join(
        render_group(group_name, names, image_paths, eliminated_set)
        for group_name, names in GROUPS.items()
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --page-bg: #f5f1e8;
      --card-bg: rgba(255, 255, 255, 0.08);
      --text: #ffffff;
      --muted: rgba(255, 255, 255, 0.85);
      --shadow: rgba(0, 0, 0, 0.18);
      --name-bg: rgba(0, 0, 0, 0.14);
      --missing-bg: rgba(255, 255, 255, 0.18);
      --stamp-red: #b40000;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: var(--page-bg);
      color: #222;
    }}

    .page {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 24px;
    }}

    .page-header {{
      text-align: center;
      margin-bottom: 24px;
    }}

    .page-header h1 {{
      margin: 0 0 8px;
      font-size: clamp(2rem, 4vw, 3.2rem);
    }}

    .page-header p {{
      margin: 0;
      color: #555;
    }}

    .tribe {{
      background: var(--tribe-bg);
      border-radius: 20px;
      padding: 24px;
      margin-bottom: 24px;
      box-shadow: 0 10px 24px var(--shadow);
    }}

    .tribe-title {{
      text-align: center;
      margin: 0 0 20px;
      font-size: clamp(2rem, 5vw, 4.5rem);
      line-height: 1;
      letter-spacing: 1px;
    }}

    .card-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 20px;
    }}

    .card {{
      display: flex;
      flex-direction: column;
      min-width: 0;
    }}

    .image-wrap {{
      position: relative;
      height: 260px;
      border-radius: 14px;
      overflow: hidden;
      background: var(--card-bg);
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .image-wrap img {{
      max-width: calc(100% - 20px);
      max-height: 100%;
      width: auto;
      height: auto;
      object-fit: contain;
      display: block;
    }}

    .missing-image {{
      color: var(--muted);
      background: var(--missing-bg);
      border: 2px dashed rgba(255, 255, 255, 0.5);
      border-radius: 12px;
      width: calc(100% - 20px);
      height: calc(100% - 20px);
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 12px;
      font-weight: bold;
    }}

    .name {{
      margin-top: 10px;
      min-height: 72px;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      color: var(--text);
      font-size: 1.8rem;
      font-weight: 700;
      padding: 10px 12px;
      border-radius: 12px;
      background: var(--name-bg);
    }}

    .eliminated .image-wrap img {{
      opacity: 0.4;
      filter: grayscale(0.15);
    }}

    .stamp {{
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%) rotate(-18deg);
      border: 4px solid var(--stamp-red);
      color: var(--stamp-red);
      background: rgba(255, 255, 255, 0.7);
      border-radius: 10px;
      padding: 10px 18px;
      font-size: 1.4rem;
      font-weight: 800;
      letter-spacing: 1px;
      white-space: nowrap;
    }}

    @media (max-width: 900px) {{
      .card-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}

    @media (max-width: 640px) {{
      .page {{
        padding: 16px;
      }}

      .tribe {{
        padding: 16px;
      }}

      .card-grid {{
        grid-template-columns: 1fr;
      }}

      .image-wrap {{
        height: 320px;
      }}

      .name {{
        font-size: 1.5rem;
      }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <header class="page-header">
      <h1>{html.escape(title)}</h1>
    </header>
    {sections_html}
  </main>
</body>
</html>
"""


def determine_eliminated(args: argparse.Namespace) -> list[str]:
    state = load_state()

    if args.clear_eliminated:
        eliminated = []
    elif args.eliminated is not None:
        eliminated = args.eliminated
    else:
        eliminated = state.get("eliminated", [])

    return eliminated


def main() -> None:
    args = parse_args()
    eliminated = determine_eliminated(args)
    output_path = PROJECT_DIR / args.output

    html_text = build_html(args.title, eliminated)
    output_path.write_text(html_text, encoding="utf-8")

    if args.save_state:
        save_state(eliminated)

    print(f"Generated {output_path.name}")
    print(f"Using state file: {STATE_FILE}")
    print(f"Eliminated: {', '.join(eliminated) if eliminated else 'none'}")


if __name__ == "__main__":
    main()
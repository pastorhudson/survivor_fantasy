# Regenerate the cheat sheet in portrait orientation without stretching images
from PIL import Image, ImageDraw, ImageFont
import os, math

# Reuse earlier extracted images
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "survivor_files")

# Map names to detected files
files = os.listdir(base)


def find_img(keyword):
    for f in files:
        if keyword.lower() in f.lower():
            return os.path.join(base, f)
    return None


def load_font(size):
    font_candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/Arial Bold.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "DejaVuSans-Bold.ttf",
    ]

    for font_path in font_candidates:
        try:
            return ImageFont.truetype(font_path, size)
        except OSError:
            continue

    raise RuntimeError("No scalable TrueType font found.")


def fit_font(draw, text, max_width, max_height, start_size):
    for size in range(start_size, 9, -2):
        font = load_font(size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        if text_w <= max_width and text_h <= max_height:
            return font, text_w, text_h, size

    font = load_font(10)
    bbox = draw.textbbox((0, 0), text, font=font)
    return font, bbox[2] - bbox[0], bbox[3] - bbox[1], 10


name_map = {
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
    "Emily": "Emily"
}

paths = {n: find_img(k) for n, k in name_map.items()}

eliminated = {
    # "Stephenie K": True,
    "Savannah": True,
    "Jenna": True,
    "Mike": True,
    "Q": True,
    "Kyle": True,
    # "Genevieve": True,
    # "Ozzy": True,
    # "Emily": True,
    # "Angelina": True,
    # "Jonathan": True,
    # "Kamilla": True,
    # "Rizo": True,
    # "Joe": True,
}

groups = {
    "Seagrens": ["Charlie", "Stephenie K", "Q", "Dee", "Coach", "Rick", "Jenna", "Christian"],
    "Youngs": ["Cirie", "Kyle", "Jonathan", "Aubry", "Angelina", "Savannah", "Chrissy", "Mike"],
    "Smiths": ["Colby Donaldson", "Kamila", "Rizo", "Geneieve", "Ozzy", "Joe", "Tiffany", "Emily"]
}

team_colors = {
    "Seagrens": "#e27648",
    "Youngs": "#60a7a1",
    "Smiths": "#6fc1d9",
}

team_name_styles = {
    "Seagrens": {"border": "#894b74", "fill": "#e1b14b"},
    "Youngs": {"border": "#cfb664", "fill": "#38764d"},
    "Smiths": {"border": "#c6e89c", "fill": "#e2719c"},
}

# Portrait layout: 3 columns
cols = 3
cell_w = 350
img_h = 260
name_h = 90
cell_h = img_h + name_h + 10

sections = []
for g, names in groups.items():
    rows = math.ceil(len(names) / cols)
    sections.append((g, names, rows))

title_h = 130
width = cols * cell_w + 40
height = sum(title_h + s[2] * cell_h + 20 for s in sections) + 40

canvas = Image.new("RGB", (width, height), (255, 255, 255))
draw = ImageDraw.Draw(canvas)

team_font = load_font(110)
name_font = load_font(40)
stamp_font = load_font(44)

y = 20

for group, names, rows in sections:
    section_top = y
    section_height = title_h + rows * cell_h + 20
    draw.rectangle(
        [(20, section_top), (width - 20, section_top + section_height)],
        fill=team_colors[group],
    )

    team_bbox = draw.textbbox((0, 0), group, font=team_font)
    team_text_w = team_bbox[2] - team_bbox[0]
    team_text_h = team_bbox[3] - team_bbox[1]
    print(f"TEAM {group!r} -> font size 110")

    team_x = (width - team_text_w) // 2
    team_y = y + (title_h - team_text_h) // 2

    team_style = team_name_styles[group]
    outline_offsets = [
        (-3, 0), (3, 0), (0, -3), (0, 3),
        (-2, -2), (-2, 2), (2, -2), (2, 2),
    ]
    for dx, dy in outline_offsets:
        draw.text(
            (team_x + dx, team_y + dy),
            group,
            team_style["border"],
            font=team_font,
        )
    draw.text((team_x, team_y), group, team_style["fill"], font=team_font)

    y += title_h

    for i, name in enumerate(names):
        col = i % cols
        row = i // cols
        x = 20 + col * cell_w
        cy = y + row * cell_h

        path = paths.get(name)
        if path and os.path.exists(path):
            im = Image.open(path).convert("RGBA")
            im.thumbnail((cell_w - 20, img_h))  # preserve aspect ratio
            px = x + (cell_w - im.width) // 2
            py = cy + (img_h - im.height) // 2

            if eliminated.get(name, False):
                overlay = Image.new("RGBA", im.size, (255, 255, 255, 160))
                im = Image.alpha_composite(im, overlay)

                stamp_layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
                stamp_draw = ImageDraw.Draw(stamp_layer)
                stamp_text = "ELIMINATED"

                text_bbox = stamp_draw.textbbox((0, 0), stamp_text, font=stamp_font)
                text_left = text_bbox[0]
                text_top = text_bbox[1]
                text_w = text_bbox[2] - text_bbox[0]
                text_h = text_bbox[3] - text_bbox[1]

                center_x = im.width // 2
                center_y = im.height // 2

                rect_w = text_w + 40
                rect_h = text_h + 24
                rect_left = center_x - rect_w // 2
                rect_top = center_y - rect_h // 2
                rect_right = center_x + rect_w // 2
                rect_bottom = center_y + rect_h // 2

                stamp_draw.rounded_rectangle(
                    [(rect_left, rect_top), (rect_right, rect_bottom)],
                    radius=10,
                    fill=(255, 255, 255, 110),
                    outline=(180, 0, 0, 255),
                    width=5,
                )

                text_x = rect_left + (rect_w - text_w) // 2 - text_left
                text_y = rect_top + (rect_h - text_h) // 2 - text_top

                stamp_draw.text(
                    (text_x, text_y),
                    stamp_text,
                    fill=(180, 0, 0, 255),
                    font=stamp_font,
                )

                rotated_stamp = stamp_layer.rotate(
                    -18,
                    resample=Image.Resampling.BICUBIC,
                    expand=False,
                )
                im = Image.alpha_composite(im, rotated_stamp)

            canvas.paste(im.convert("RGB"), (px, py))

        name_bbox = draw.textbbox((0, 0), name, font=name_font)
        name_text_w = name_bbox[2] - name_bbox[0]
        name_text_h = name_bbox[3] - name_bbox[1]
        print(f"NAME {name!r} -> font size 40")

        name_x = x + (cell_w - name_text_w) // 2
        name_y = cy + img_h + (name_h - name_text_h) // 2
        draw.text((name_x, name_y), name, (255, 255, 255), font=name_font)

    y += rows * cell_h + 20

out = "survivor50_cheatsheet_portrait.png"
canvas.save(out)

out
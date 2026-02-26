"""Generate app.ico for the executable. Used by build.py."""
from pathlib import Path

def generate_icon(out_path: Path) -> None:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        raise SystemExit("Install Pillow for icon generation: pip install Pillow")

    sizes = [(256, 256), (48, 48), (32, 32), (16, 16)]
    images = []

    for w, h in sizes:
        scale = w / 256
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Chat bubble (rounded rect) - WhatsApp green
        pad = max(1, int(18 * scale))
        xy = [pad, pad, w - pad, h - pad]
        r = max(2, int(24 * scale))
        draw.rounded_rectangle(xy, radius=r, fill=(37, 211, 102), outline=(32, 180, 90), width=max(1, int(3 * scale)))
        # Small "document" corner (page fold) - white
        fold = max(2, int(28 * scale))
        doc_x = w - fold - max(2, int(12 * scale))
        doc_y = pad
        doc_w = fold
        doc_h = int(36 * scale)
        draw.rounded_rectangle([doc_x, doc_y, doc_x + doc_w, doc_y + doc_h], radius=max(1, int(4 * scale)), fill=(255, 255, 255, 230))
        images.append(img)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(out_path, format="ICO", append_images=images[1:])

if __name__ == "__main__":
    generate_icon(Path(__file__).parent / "app.ico")

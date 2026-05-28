"""Generiert icon16.png, icon48.png, icon128.png aus icon.svg.
Benötigt: pip install cairosvg  ODER  pip install Pillow
Ausführen: python extension/icons/generate_icons.py
"""
import sys
from pathlib import Path

ICONS_DIR = Path(__file__).parent
SVG_PATH = ICONS_DIR / 'icon.svg'
SIZES = [16, 48, 128]


def generate_with_cairosvg():
    import cairosvg
    for size in SIZES:
        cairosvg.svg2png(
            url=str(SVG_PATH),
            write_to=str(ICONS_DIR / f'icon{size}.png'),
            output_width=size,
            output_height=size,
        )
        print(f'  icon{size}.png erstellt')


def generate_with_pillow():
    from PIL import Image
    import io

    try:
        import cairosvg
        generate_with_cairosvg()
        return
    except ImportError:
        pass

    # Fallback: einfache farbige Platzhalter-Icons
    for size in SIZES:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        pixels = img.load()
        bg = (26, 26, 46, 255)
        fg = (123, 104, 238, 255)

        # Hintergrund mit abgerundeten Ecken
        r = max(2, size // 6)
        for y in range(size):
            for x in range(size):
                in_corner = (
                    (x < r and y < r and (x - r) ** 2 + (y - r) ** 2 > r * r) or
                    (x >= size - r and y < r and (x - (size - r - 1)) ** 2 + (y - r) ** 2 > r * r) or
                    (x < r and y >= size - r and (x - r) ** 2 + (y - (size - r - 1)) ** 2 > r * r) or
                    (x >= size - r and y >= size - r and (x - (size - r - 1)) ** 2 + (y - (size - r - 1)) ** 2 > r * r)
                )
                pixels[x, y] = (0, 0, 0, 0) if in_corner else bg

        # Einfaches Cursor-Symbol
        pad = max(2, size // 8)
        cw = size - 2 * pad
        ch = size - 2 * pad
        # Dreieck (vereinfacht als gefüllter Bereich)
        for y in range(ch):
            w = int(cw * 0.6 * (1 - y / ch)) + 1
            for x in range(w):
                px = pad + x
                py = pad + y
                if 0 <= px < size and 0 <= py < size:
                    pixels[px, py] = fg

        img.save(str(ICONS_DIR / f'icon{size}.png'))
        print(f'  icon{size}.png erstellt (Pillow-Fallback)')


if __name__ == '__main__':
    print('Generiere Icons...')
    try:
        generate_with_pillow()
        print('Fertig!')
    except ImportError:
        print('Fehler: Bitte Pillow installieren:  pip install Pillow')
        sys.exit(1)

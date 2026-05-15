import argparse
import json
from pathlib import Path

import fontforge  # type: ignore


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--font-path", default=".", help="Font path")
    parser.add_argument("-o", "--output", default="output.json", help="Output file")

    args = parser.parse_args()
    font_path = args.font_path

    font = fontforge.open(font_path)

    data = {"em": font.em, "ascent": font.ascent, "chars": []}

    for glyph in font.glyphs():
        if glyph.unicode == -1:
            continue

        char = chr(glyph.unicode)

        x_min, y_min, x_max, y_max = glyph.boundingBox()

        data["chars"].append(
            {
                "char": char,
                "unicode": glyph.unicode,
                "box": {
                    "x_min": x_min,
                    "y_min": y_min,
                    "x_max": x_max,
                    "y_max": y_max,
                },
            }
        )

    Path(args.output).write_text(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()

import argparse
import json
from pathlib import Path

import fontforge  # type: ignore


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", default=".", help="Font dir")
    parser.add_argument("-o", "--output", default="output.json", help="Output file")

    args = parser.parse_args()
    font_dir = Path(args.dir)
    output = {}
    for path in font_dir.glob("*.ttf"):
        font = fontforge.open(path.as_posix())
        output[path.as_posix()] = font.familyname

    output_path = Path(args.output)
    output_path.write_text(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

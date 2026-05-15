import argparse
from pathlib import Path

from hat.pdf_to_boxes.pdf_to_boxes import PdfToBoxes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file-path", type=Path, required=True, help="PDF file")
    parser.add_argument("-r", "--resolution", type=int, help="Resolution")
    parser.add_argument("-p", "--page-index", type=int, help="Page index")

    args = parser.parse_args()

    pdf_to_boxes = PdfToBoxes(
        file_path=args.file_path, resolution=args.resolution, page_index=args.page_index
    )
    pdf_to_boxes.convert()


if __name__ == "__main__":
    main()

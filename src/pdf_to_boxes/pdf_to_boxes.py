import json
import subprocess
import tempfile
from collections.abc import Generator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pdfplumber

from PIL import ImageDraw

from hat.pdf_to_boxes.models.box import Box
from hat.pdf_to_boxes.models.font_box import FontBox
from hat.pdf_to_boxes.models.units.font_path import FontPath
from hat.pdf_to_boxes.models.units.font_name import FontName
from hat.pdf_to_boxes.models.units.em import Em
from hat.pdf_to_boxes.models.units.em2pt import Em2Pt
from hat.pdf_to_boxes.models.units.pt import Pt
from hat.pdf_to_boxes.models.units.pt2px import Pt2Px
from hat.pdf_to_boxes.models.units.px import Px


def find_font_path(
    mapping: Mapping[FontPath, FontName], font_name: FontName
) -> Path | None:
    for fp, fn in mapping.items():
        if font_name == fn:
            return Path(fp)
    return None


@lru_cache
def load_font_info(font_dir: Path, fontname: str) -> FontBox:
    font_mapping = PdfToBoxes.create_mapping_fontname(font_dir)
    font_path = find_font_path(font_mapping, FontName(fontname))
    assert font_path is not None
    return PdfToBoxes.load_font_info(font_path)


@dataclass
class PdfToBoxes:
    file_path: Path
    resolution: int
    page_index: int

    def read(self) -> list[Box[Px]]:
        boxes: list[Box[Px]] = []
        pdf = pdfplumber.open(self.file_path.as_posix())
        page = pdf.pages[self.page_index]
        image = page.to_image(resolution=self.resolution)

        for char in page.objects["char"]:
            box: Box[Px] = Box(
                x=Pt2Px(pt=Pt(char["x0"]), dpi=self.resolution),
                y=Pt2Px(Pt(page.height), self.resolution)
                - Pt2Px(Pt(char["y1"]), self.resolution),
                w=Pt2Px(Pt(char["width"]), self.resolution),
                h=Pt2Px(Pt(char["height"]), self.resolution),
                label=char["text"],
                fontname=char["fontname"],
                font_size=char["size"],
            )
            # draw = ImageDraw.Draw(image.original)
            # PdfToBoxes.draw_box(draw, box)
            boxes.append(box)
        return boxes

    def debug_boxes(self, page_index: int, boxes: list[Box[Px]]):
        pdf = pdfplumber.open(self.file_path.as_posix())
        page = pdf.pages[page_index]
        image = page.to_image(resolution=self.resolution)
        for box in boxes:
            draw = ImageDraw.Draw(image.original)
            PdfToBoxes.draw_box(draw, box)

    @staticmethod
    def draw_box(draw, box: Box[Px]):
        draw.rectangle(
            [(box.x, box.y), (box.x + box.w, box.y + box.h)],
            outline="red",
            width=1,
        )

    @contextmanager
    def extract_font(self) -> Generator[Path, None, None]:
        with tempfile.TemporaryDirectory() as temp_dir:
            subprocess.run(
                ["mutool", "extract", self.file_path.as_posix()], cwd=temp_dir
            )
            yield Path(temp_dir)

    @staticmethod
    def create_mapping_fontname(font_dir: Path) -> Mapping[FontPath, FontName]:
        with tempfile.NamedTemporaryFile(suffix=".output.json") as temp_file:
            subprocess.run(
                [
                    "fontforge",
                    "-script",
                    Path("../fontforge_scripts/fontname_mapping.py")
                    .absolute()
                    .as_posix(),
                    "-d",
                    font_dir.as_posix(),
                    "-o",
                    temp_file.name,
                ]
            )
            temp_path = Path(temp_file.name)
            assert temp_path.exists()
            return json.loads(temp_path.read_text())

    @staticmethod
    def load_font_info(font_path: Path) -> FontBox[float]:
        with tempfile.NamedTemporaryFile(suffix=".output.json") as temp_file:
            subprocess.run(
                [
                    "fontforge",
                    "-script",
                    Path("../fontforge_scripts/font_info.py").absolute().as_posix(),
                    "-f",
                    font_path.as_posix(),
                    "-o",
                    temp_file.name,
                ]
            )
            temp_path = Path(temp_file.name)
            assert temp_path.exists()
            return FontBox.model_validate_json(temp_path.read_text())

    def convert(self):
        boxes = self.read()

        with self.extract_font() as font_dir:
            for box in boxes:
                font_box = load_font_info(font_dir, box.fontname)
                for char in font_box.chars:
                    label = char.char
                    if label == box.label:
                        x_min = char.box.x_min
                        y_min = char.box.y_min
                        x_max = char.box.x_max
                        y_max = char.box.y_max

                        x_min_px = Pt2Px(
                            pt=Em2Pt(
                                em=Em(x_min),
                                font_size=box.font_size,
                                em_size=Em(font_box.em),
                            ),
                            dpi=self.resolution,
                        )
                        y_min_px = Pt2Px(
                            pt=Em2Pt(
                                em=Em(y_min),
                                font_size=box.font_size,
                                em_size=Em(font_box.em),
                            ),
                            dpi=self.resolution,
                        )
                        x_max_px = Pt2Px(
                            pt=Em2Pt(
                                em=Em(x_max),
                                font_size=box.font_size,
                                em_size=Em(font_box.em),
                            ),
                            dpi=self.resolution,
                        )
                        y_max_px = Pt2Px(
                            pt=Em2Pt(
                                em=Em(y_max),
                                font_size=box.font_size,
                                em_size=Em(font_box.em),
                            ),
                            dpi=self.resolution,
                        )

                        width = x_max_px - x_min_px
                        height = y_max_px - y_min_px
                        x = box.x + x_min_px
                        y = (
                            box.y
                            + Pt2Px(
                                pt=Em2Pt(
                                    em=Em(font_box.ascent),
                                    font_size=box.font_size,
                                    em_size=Em(font_box.em),
                                ),
                                dpi=self.resolution,
                            )
                            - y_max_px
                        )
                        box.x = x
                        box.y = y
                        box.w = width
                        box.h = height

        self.debug_boxes(0, boxes)

from hat.pdf_to_boxes.models.units.pt import Pt
from hat.pdf_to_boxes.models.units.px import Px


class Pt2Px(Px):
    def __init__(self, pt: Pt, dpi: float):
        super().__init__(pt.value * dpi / 72)

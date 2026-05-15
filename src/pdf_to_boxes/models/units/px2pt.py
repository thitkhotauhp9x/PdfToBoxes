from hat.pdf_to_boxes.models.units.pt import Pt
from hat.pdf_to_boxes.models.units.px import Px


class Px2Pt(Pt):
    def __init__(self, px: Px, dpi: float):
        super().__init__(px.value * 72 / dpi)

from hat.pdf_to_boxes.models.units.em import Em
from hat.pdf_to_boxes.models.units.pt import Pt


class Em2Pt(Pt):
    def __init__(self, em: Em, font_size: float, em_size: Em):
        super().__init__(em.value * font_size / em_size.value)

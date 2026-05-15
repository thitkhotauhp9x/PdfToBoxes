from dataclasses import dataclass


@dataclass
class Box[T]:
    x: T
    y: T
    w: T
    h: T
    label: str
    fontname: str
    font_size: float

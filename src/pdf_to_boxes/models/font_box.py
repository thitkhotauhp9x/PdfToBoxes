from pydantic import BaseModel


class Box[T](BaseModel):
    x_min: T
    y_min: T
    x_max: T
    y_max: T


class Character[T](BaseModel):
    char: str
    unicode: int
    box: Box[T]


class FontBox[T](BaseModel):
    em: float
    ascent: float
    chars: list[Character[T]]

class Px:
    def __init__(self, value: float) -> None:
        self._value = value

    @property
    def value(self) -> float:
        return self._value

    def __add__(self, other: "Px") -> "Px":
        return Px(self.value + other.value)

    def __sub__(self, other: "Px") -> "Px":
        return Px(self.value - other.value)

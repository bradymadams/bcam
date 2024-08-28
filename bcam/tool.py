import math


class Tool:
    pass


class EndMill(Tool):
    def __init__(self, diameter: float) -> None:
        self._diameter = diameter

    @property
    def diameter(self) -> float:
        return self._diameter

    @property
    def radius(self) -> float:
        return self._diameter * 0.5


class TaperMill(Tool):
    def __init__(
        self, angle_degrees: float = 45.0, height: float | None = None
    ) -> None:
        self._angle = angle_degrees
        self._height = height

    @property
    def angle_degrees(self) -> float:
        return self._angle

    @property
    def angle_radians(self) -> float:
        return self._angle * math.pi / 180.0

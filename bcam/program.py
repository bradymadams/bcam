import dataclasses
from collections.abc import Generator

from bcam.tool import Tool

Coord = float | None
Feed = float | None


@dataclasses.dataclass
class Config:
    rapid_feed: float = 1000.0
    cut_feed: float = 1000.0


class _Operation:
    def gcode(self) -> list[str]:
        raise NotImplementedError

    def format_arg(self, arg: str, value: float | None) -> str:
        return f" {arg}{value}" if value is not None else ""
        # return f" {arg}{value:7.2f}" if value is not None else ""


class _Comment(_Operation):
    def __init__(self, text: str) -> None:
        self._text = text

    def gcode(self) -> list[str]:
        return [f"; {self._text}"]


class _Move(_Operation):
    def __init__(
        self,
        x: Coord = None,
        y: Coord = None,
        z: Coord = None,
        feed: Feed = None,
        rapid: bool = False,
    ) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.feed = feed
        self.rapid = rapid

    def gcode(self) -> list[str]:
        code = 0 if self.rapid else 1
        x = self.format_arg("X", self.x)
        y = self.format_arg("Y", self.y)
        z = self.format_arg("Z", self.z)
        f = self.format_arg("F", self.feed)

        return [f"G{code}{x}{y}{z}{f}"]


class _Arc(_Operation):
    def __init__(
        self,
        i: Coord,
        j: Coord,
        x: Coord,
        y: Coord,
        feed: Feed = None,
        clockwise: bool = True,
    ) -> None:
        self.i = i
        self.j = j
        self.x = x
        self.y = y
        self.feed = feed
        self.clockwise = clockwise

    def gcode(self) -> list[str]:
        code = 2 if self.clockwise else 3
        x = self.format_arg("X", self.x)
        y = self.format_arg("Y", self.y)
        i = self.format_arg("I", self.i)
        j = self.format_arg("J", self.j)
        f = self.format_arg("F", self.feed)

        return ["G17", f"G{code}{x}{y}{i}{j}{f}"]


def _coordinates_from_delta(
    pos: tuple[float, float, float],
    dx: Coord = None,
    dy: Coord = None,
    dz: Coord = None,
) -> tuple[Coord, Coord, Coord]:
    x = pos[0] + dx if dx else None
    y = pos[1] + dy if dy else None
    z = pos[2] + dz if dz else None

    return x, y, z


# TODO rename to Path and make a new Program class that can be multiple Paths
class Program:
    def __init__(
        self,
        tool: Tool,
        name: str = "default",
        config: Config | None = None,
        home: bool = True,
    ) -> None:
        self._tool = tool
        self._name = name
        self._operations: list[_Operation] = [_Comment(f"({self._name})")]
        self._pos = (0.0, 0.0, 0.0)
        self._config = config or Config()

        if home:
            self.home()

    def __iter__(self) -> Generator[_Operation]:
        yield from self._operations

    def _set_position(self, x: Coord = None, y: Coord = None, z: Coord = None) -> None:
        self._pos = (x or self._pos[0], y or self._pos[1], z or self._pos[2])

    @property
    def tool(self) -> Tool:
        return self._tool

    def home(self) -> None:
        return self.rapid(x=0.0, y=0.0, z=0.0)

    def _move(self, x: Coord, y: Coord, z: Coord, feed: Feed, rapid: bool) -> None:
        self._operations.append(_Move(x, y, z, feed, rapid))
        self._set_position(x, y, z)

    def rapid(
        self, *, x: Coord = None, y: Coord = None, z: Coord = None, feed: Feed = None
    ) -> None:
        self._move(x, y, z, feed or self._config.rapid_feed, rapid=True)

    def drapid(
        self, *, dx: Coord = None, dy: Coord = None, dz: Coord = None, feed: Feed = None
    ) -> None:
        x, y, z = _coordinates_from_delta(self._pos, dx, dy, dz)
        return self.rapid(x=x, y=y, z=z, feed=feed)

    def cut(
        self, *, x: Coord = None, y: Coord = None, z: Coord = None, feed: Feed = None
    ) -> None:
        self._move(x, y, z, feed or self._config.cut_feed, rapid=False)

    def dcut(
        self, *, dx: Coord = None, dy: Coord = None, dz: Coord = None, feed: Feed = None
    ) -> None:
        x, y, z = _coordinates_from_delta(self._pos, dx, dy, dz)
        return self.cut(x=x, y=y, z=z, feed=feed)

    def cut_circle(
        self, *, xc: float, yc: float, feed: Feed = None, clockwise: bool = True
    ) -> None:
        # Start and end position are the same, so no need to call _set_position
        self._operations.append(
            _Arc(
                xc - self._pos[0],
                yc - self._pos[1],
                self._pos[0],
                self._pos[1],
                feed or self._config.cut_feed,
                clockwise,
            )
        )

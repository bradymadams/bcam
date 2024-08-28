import enum
from typing import Literal, TextIO

from bcam.program import Program


class Command:
    pass


class Flavor(enum.Enum):
    grbl = 1


CoordSystem = Literal[54, 55, 56, 57, 58, 59]


class Writer:
    def __init__(self, flavor: Flavor = Flavor.grbl) -> None:
        # TODO should be handled in Operation.gcode?
        # If so, Flavor definition needs to move.
        self._flavor = flavor

    def lines(self, prog: Program, coord_system: CoordSystem = 54) -> list[str]:
        lines = ["G21", f"G{coord_system}", "G90", "G94"]

        for op in prog:
            lines.extend(op.gcode())

        return lines

    def write(self, out: TextIO, prog: Program, coord_system: CoordSystem = 54) -> None:
        lines = self.lines(prog, coord_system)

        for ln in lines:
            out.write(ln)
            out.write("\n")

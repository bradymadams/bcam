import io
import pytest

import bcam


class _DummyTool(bcam.tool.Tool):
    pass


@pytest.fixture
def program() -> bcam.program.Program:
    prog = bcam.program.Program()

    p1 = prog.add_path(bcam.path.Path(_DummyTool()))
    p1.home()
    p1.rapid(x=100.0)
    p1.cut(y=50.0)
    p1.drapid(dz=1.0, feed=20.0)

    return prog


def test_lines(program: bcam.program.Program) -> None:
    lines = bcam.gcode.Writer().lines(program, 55)

    assert lines == [
        "G21",
        "G55",
        "G90",
        "G94",
        "; (default)",
        "G0 X0.0 Y0.0 Z0.0 F1000.0",
        "G0 X100.0 F1000.0",
        "G1 Y50.0 F1000.0",
        "G0 Z1.0 F20.0",
    ]


def test_write(program: bcam.program.Program) -> None:
    out = io.StringIO()
    bcam.gcode.Writer().write(out, program)

    out.seek(0)
    lines = out.readlines()

    assert lines == [
        "G21\n",
        "G54\n",
        "G90\n",
        "G94\n",
        "; (default)\n",
        "G0 X0.0 Y0.0 Z0.0 F1000.0\n",
        "G0 X100.0 F1000.0\n",
        "G1 Y50.0 F1000.0\n",
        "G0 Z1.0 F20.0\n",
    ]

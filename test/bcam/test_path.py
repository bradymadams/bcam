import pytest

import bcam

from .helpers import get_path_non_comment_operations


class _DummyTool(bcam.tool.Tool):
    pass


@pytest.mark.parametrize(
    "x, y, z, f, rapid, expected",
    [
        # Normal moves with full coordinates
        (0.5, 1.0, 2.0, 100.0, False, ["G1 X0.5 Y1.0 Z2.0 F100.0"]),
        (0.0, 0.0, 0.0, 50.0, False, ["G1 X0.0 Y0.0 Z0.0 F50.0"]),
        (10.5, -3.2, 5.7, 200.0, False, ["G1 X10.5 Y-3.2 Z5.7 F200.0"]),
        (-1.5, 2.5, -0.5, 75.5, False, ["G1 X-1.5 Y2.5 Z-0.5 F75.5"]),
        # Rapid moves (with or without feed rate)
        (0.5, 1.0, 2.0, 100.0, True, ["G0 X0.5 Y1.0 Z2.0 F100.0"]),
        (10.5, -3.2, 5.7, None, True, ["G0 X10.5 Y-3.2 Z5.7"]),
        (0.5, 1.0, 2.0, None, True, ["G0 X0.5 Y1.0 Z2.0"]),
        # Moves with None coordinates
        (None, 1.0, 2.0, 100.0, False, ["G1 Y1.0 Z2.0 F100.0"]),
        (0.5, None, 2.0, 100.0, False, ["G1 X0.5 Z2.0 F100.0"]),
        (0.5, 1.0, None, 100.0, False, ["G1 X0.5 Y1.0 F100.0"]),
        # Moves with None feed rate
        (0.5, 1.0, 2.0, None, False, ["G1 X0.5 Y1.0 Z2.0"]),
        # Complex combinations of None and rapid
        (0.5, None, 2.0, None, True, ["G0 X0.5 Z2.0"]),
    ],
)
def test_move(
    x: float | None,
    y: float | None,
    z: float | None,
    f: float | None,
    rapid: bool,
    expected: list[str],
) -> None:
    op = bcam.path._Move(x, y, z, f, rapid=rapid)
    assert op.gcode() == expected


@pytest.mark.parametrize(
    "i, j, x, y, feed, clockwise, expected",
    [
        # Full arc specifications
        (1.0, 2.0, 3.0, 4.0, 100.0, True, ["G17", "G2 X3.0 Y4.0 I1.0 J2.0 F100.0"]),
        (0.5, -1.5, 2.5, -0.5, 50.0, False, ["G17", "G3 X2.5 Y-0.5 I0.5 J-1.5 F50.0"]),
        # Arcs with None feed rate
        (1.0, 2.0, 3.0, 4.0, None, True, ["G17", "G2 X3.0 Y4.0 I1.0 J2.0"]),
        # Arcs with None coordinates
        (None, 2.0, 3.0, 4.0, 100.0, True, ["G17", "G2 X3.0 Y4.0 J2.0 F100.0"]),
        (1.0, None, 3.0, 4.0, 100.0, True, ["G17", "G2 X3.0 Y4.0 I1.0 F100.0"]),
        # Different arc directions
        (1.0, 2.0, 3.0, 4.0, 200.0, False, ["G17", "G3 X3.0 Y4.0 I1.0 J2.0 F200.0"]),
    ],
)
def test_arc(
    i: float | None,
    j: float | None,
    x: float | None,
    y: float | None,
    feed: float | None,
    clockwise: bool,
    expected: list[str],
) -> None:
    op = bcam.path._Arc(i, j, x, y, feed, clockwise)
    assert op.gcode() == expected


def test_path_rapid() -> None:
    path = bcam.path.Path(_DummyTool(), config=bcam.path.Config(rapid_feed=500.0))
    path.rapid(x=100.0, y=10.0, z=1.0)
    path.drapid(dx=-10.0, dz=0.5, feed=40.0)

    ops = get_path_non_comment_operations(path)

    assert len(ops) == 2

    assert ops[0].gcode() == ["G0 X100.0 Y10.0 Z1.0 F500.0"]
    assert ops[1].gcode() == ["G0 X90.0 Z1.5 F40.0"]


def test_path_cut() -> None:
    path = bcam.path.Path(_DummyTool(), config=bcam.path.Config(cut_feed=600.0))
    path.cut(x=100.0, y=10.0, z=1.0)
    path.dcut(dx=-10.0, dy=0.5, feed=40.0)

    ops = get_path_non_comment_operations(path)

    assert len(ops) == 2

    assert ops[0].gcode() == ["G1 X100.0 Y10.0 Z1.0 F600.0"]
    assert ops[1].gcode() == ["G1 X90.0 Y10.5 F40.0"]


def test_path_home() -> None:
    path = bcam.path.Path(
        _DummyTool(), config=bcam.path.Config(rapid_feed=800.0, cut_feed=600.0)
    )
    path.cut(x=100.0, y=10.0, z=1.0)
    path.home()

    ops = get_path_non_comment_operations(path)

    assert ops[0].gcode() == ["G1 X100.0 Y10.0 Z1.0 F600.0"]
    assert ops[1].gcode() == ["G0 X0.0 Y0.0 Z0.0 F800.0"]


@pytest.mark.parametrize(
    "start_x, start_y, start_z, center_x, center_y, feed, clockwise, expected_gcode",
    [
        # Normal circle at origin, default feed rate, clockwise
        (0.0, 0.0, 0.0, 1.0, 1.0, None, True, ["G17", "G2 X0.0 Y0.0 I1.0 J1.0 F600.0"]),
        # Circle at non-zero position with specific feed rate
        (
            2.0,
            3.0,
            1.0,
            5.0,
            7.0,
            100.0,
            True,
            ["G17", "G2 X2.0 Y3.0 I3.0 J4.0 F100.0"],
        ),
        # Counterclockwise circle with specific feed rate
        (
            2.0,
            3.0,
            1.0,
            5.0,
            6.0,
            100.0,
            False,
            ["G17", "G3 X2.0 Y3.0 I3.0 J3.0 F100.0"],
        ),
    ],
)
def test_cut_circle(
    start_x: float,
    start_y: float,
    start_z: float,
    center_x: float,
    center_y: float,
    feed: float | None,
    clockwise: bool,
    expected_gcode: list[str],
) -> None:
    path = bcam.path.Path(_DummyTool(), config=bcam.path.Config(cut_feed=600.0))
    path.cut(x=start_x, y=start_y, z=start_z)
    path.cut_circle(xc=center_x, yc=center_y, feed=feed, clockwise=clockwise)
    ops = get_path_non_comment_operations(path)

    assert len(ops) == 2
    assert ops[1].gcode() == expected_gcode

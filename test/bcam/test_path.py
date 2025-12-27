import pytest

import bcam


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

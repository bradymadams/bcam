import bcam


class _DummyTool(bcam.tool.Tool):
    pass


def test_add_path() -> None:
    prog = bcam.program.Program()
    p1 = bcam.path.Path(_DummyTool())
    p2 = prog.add_path(p1)

    assert len(prog.paths) == 1
    assert p2 is p1


def test_iter_operations() -> None:
    prog = bcam.program.Program()

    p1 = prog.add_path(bcam.path.Path(_DummyTool()))
    p1.rapid(x=100.0)

    p2 = prog.add_path(bcam.path.Path(_DummyTool()))
    p2.cut(x=50.0)

    ops = list(prog)

    assert len(ops) == 4
    assert ops[0].gcode()[0].startswith(";")
    assert ops[1].gcode() == ["G0 X100.0 F1000.0"]
    assert ops[2].gcode()[0].startswith(";")
    assert ops[3].gcode() == ["G1 X50.0 F1000.0"]

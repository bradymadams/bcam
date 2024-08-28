from bcam.program import Program
from bcam.tool import EndMill


def cut_hole(
    prog: Program,
    diameter: float,
    x: float,
    y: float,
    ztop: float,
    zbot: float,
    zsafe: float,
    dz: float | None = None,
    clockwise: bool = True,
) -> None:
    if not isinstance(prog.tool, EndMill):
        raise Exception("cut_hole requires an EndMill tool")

    if ztop <= zbot:
        raise Exception("ztop must be greater than zbot")

    if diameter < prog.tool.diameter:
        raise Exception(
            "Tool diameter ({prog.tool.diameter}) is greater "
            "than hole diameter ({diameter})"
        )

    if diameter == prog.tool.diameter:
        raise Exception("TODO need to implement plunge hole cut")

    prog.rapid(z=zsafe)
    prog.rapid(x=x, y=(y + diameter / 2 - prog.tool.radius))

    if dz is None or dz == 0.0:
        dz = ztop - zbot

    dz = abs(dz)

    z = ztop - dz
    while True:
        prog.cut(z=z)
        prog.cut_circle(xc=x, yc=y, clockwise=clockwise)

        if z <= zbot:
            break

        z = max(zbot, z - dz)

    prog.rapid(z=zsafe)


def transform_bcnc_probe_file(
    probe_path: str, probe_out: str, dx: float, dy: float
) -> None:

    probe_config = []
    probe_points = []
    with open(probe_path) as f:
        for _ in range(3):
            c = f.readline().split()
            assert len(c) == 3  # noqa: S101
            probe_config.append([float(c[0]), float(c[1]), int(c[2])])

        nx = probe_config[0][2]
        ny = probe_config[1][2]

        # Empty line
        f.readline()

        for _ in range(ny):
            # Empty line before each block
            f.readline()

            for __ in range(nx):
                c = f.readline().split()
                assert len(c) == 3  # noqa: S101
                probe_points.append([float(x) for x in c])

    probe_config[0][0] += dx
    probe_config[0][1] += dx

    probe_config[1][0] += dy
    probe_config[1][1] += dy

    for pt in probe_points:
        pt[0] += dx
        pt[1] += dy

    def _vals_line(vals: list[float | int]) -> str:
        return " ".join([str(v) for v in vals]) + "\n"

    with open(probe_out, "w") as f:
        f.write(_vals_line(probe_config[0]))
        f.write(_vals_line(probe_config[1]))
        f.write(_vals_line(probe_config[2]))
        f.write("\n")

        for j in range(ny):
            f.write("\n")
            for i in range(nx):
                f.write(_vals_line(probe_points[j * nx + i]))

        f.write("\n")

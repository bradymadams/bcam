from collections.abc import Generator

from bcam.path import Operation, Path


class Program:
    """A collection of Path objects that can be converted to G-code."""

    def __init__(self, name: str = "program") -> None:
        self._name = name
        self._paths: list[Path] = []

    def __iter__(self) -> Generator[Operation, None, None]:
        """Iterate through all operations in all paths."""
        for path in self._paths:
            yield from path

    @property
    def name(self) -> str:
        return self._name

    @property
    def paths(self) -> list[Path]:
        return self._paths

    def add_path(self, path: Path) -> Path:
        """Add a path to the program."""
        self._paths.append(path)
        return path

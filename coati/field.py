from typing import Any


class Field:
    def __init__(
        self, __type: type, __name: str, /, default: Any | None = None
    ) -> None:
        self._type = __type
        self._name = __name
        self.default = default

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return self._name

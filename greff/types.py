import enum


class UnsetType(enum.Enum):
    UNSET = enum.auto()

    def __str__(self) -> str:
        return self.name


UNSET = UnsetType.UNSET

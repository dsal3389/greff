from __future__ import annotations
from typing import TYPE_CHECKING, Any
from .typing import get_grahpql_ref
from .types import UnsetType, UNSET

if TYPE_CHECKING:
    from .type import Type


class Field:
    def __init__(
        self,
        __type: type | UnsetType = UNSET,
        __name: str | UnsetType = UNSET,
        /,
        default: Any | UnsetType = UNSET,
    ) -> None:
        self.default = default
        self._name = __name
        self._referenced_graphql_type = None

        if __type is not UNSET:
            self.set_field_type(__type)

    @property
    def name(self) -> str | UnsetType:
        return self._name

    @property
    def __queryname__(self) -> str:
        if not self.is_graphql_reference:
            raise TypeError(
                f"field does not support `__queryname__` since type doesn't reference a graphql type"
            )
        return self.name

    @property
    def type_(self) -> type | UnsetType:
        return getattr(self, "_type", UNSET)

    @property
    def is_graphql_reference(self) -> bool:
        return self._referenced_graphql_type is not None

    @property
    def referenced_graphql_type(self) -> Type | None:
        return self._referenced_graphql_type

    def set_field_type(self, type_: type) -> None:
        if self.type_ is not UNSET:
            raise TypeError(
                f"cannot set a type for a field more then once, type for field `{self.name}` already set to `{self._type}`"
            )
        self._type = type_
        self._referenced_graphql_type = get_grahpql_ref(self._type)

    def get_default(self) -> Any:
        return self.default

    def __str__(self) -> str:
        return self._name

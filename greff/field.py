from __future__ import annotations
from typing import TYPE_CHECKING, Any
from .typing import get_grahpql_ref

if TYPE_CHECKING:
    from .type import Type


class Field:
    def __init__(
        self, __type: type, __name: str, /, default: Any | None = None
    ) -> None:
        self._type = __type
        self._name = __name
        self._referenced_graphql_type = get_grahpql_ref(self._type)
        self.default = default

    @property
    def name(self) -> str:
        return self._name

    @property
    def type_(self) -> type:
        return self._type
    
    @property
    def is_graphql_reference(self) -> bool:
        return self._referenced_graphql_type is not None

    @property
    def referenced_graphql_type(self) -> Type | None:
        return self._referenced_graphql_type

    def __str__(self) -> str:
        return self._name

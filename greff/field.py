from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, get_origin, get_args
from .typing import TypesWithArgs
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
        serializer: Callable | None = None
    ) -> None:
        self.default = default
        self._name = __name
        self._referenced_graphql_type = None
        self._iterable = False
        self._serializer = serializer
        
        if __type is not UNSET:
            self.set_field_type(__type)

    @property
    def name(self) -> str | UnsetType:
        return self._name

    @property
    def type_(self) -> type | UnsetType:
        return getattr(self, "_type", UNSET)

    @property
    def referenced_graphql_type(self) -> Type | None:
        return self._referenced_graphql_type
    
    @property
    def iterable(self) -> bool:
        return self._iterable

    def set_field_type(self, type_: type) -> None:
        if self.type_ is not UNSET:
            raise TypeError(
                f"cannot set a type for a field more then once, type for field `{self.name}` already set to `{self._type}`"
            )
        self._type = type_
        self._analyze_type(self._type)

    def serialize_value(self, value: Any) -> Any:
        if self._serializer is not None:
            return self._serializer(self, value)
        return value

    def get_default(self) -> Any:
        return self.default

    def __str__(self) -> str:
        return self._name

    def _analyze_type(self, type_: type) -> None:
        from .type import Type

        if type(type_) not in TypesWithArgs:
            if issubclass(type_, Type):
                self._referenced_graphql_type = type_
            return 

        origin = get_origin(type_)

        if origin in (list, tuple, set):
            self._iterable = True

        for arg in get_args(type_):
            self._analyze_type(arg)

        

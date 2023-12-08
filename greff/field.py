from __future__ import annotations
from collections.abc import Iterable as IterableInterface
from typing import TYPE_CHECKING, Any, Callable, get_origin, get_args
from .typing import TypesWithArgs
from .types import UnsetType, UNSET

if TYPE_CHECKING:
    from .type import Type


class Field:
    def __init__(
        self,
        *,
        default: Any | UnsetType = UNSET,
        serializer: Callable | None = None,
        queryable: bool = True,
        query_name: str | None = UNSET,
        mutable: bool = True,
        mutate_name: str | None = UNSET,
    ) -> None:
        self.default = default
        self._name = UNSET
        self._type = None
        self._query_name = query_name
        self._mutate_name = mutate_name

        self._queryable = queryable
        self._mutable = mutable
        self._serializer = serializer

        self._iterable = False
        self._allow_raw_dict = False

    @property
    def name(self) -> str | UnsetType:
        return self._name
    
    @property
    def type(self) -> type | None:
        return self._type
    
    @property
    def query_name(self) -> str:
        return self._query_name

    @property
    def mutate_name(self) -> str:
        return self._mutate_name
    
    @property
    def iterable(self) -> bool:
        return self._iterable

    @property
    def is_type_graphql(self) -> bool:
        from .type import Type
        return bool(self._type and issubclass(self._type, Type))
    
    def get_default(self) -> Any:
        return self.default

    def validate_value(self, graphlq_type: type[Type], value: Any) -> bool:
        if self._iterable and not issubclass(type(value), IterableInterface):
            raise TypeError(
                f"`{graphlq_type.__name__}.{self.name}` should be a list of graphql types, but graphql returned type `{type(value).__name__}`"
            )
        elif isinstance(value, dict) and (not self._allow_raw_dict and not self.is_type_graphql):
            raise TypeError(
                f"`{graphlq_type.__name__}.{self.name}` is a dict, but field does not accept dict nor doesn't reference any sub graphql field"
            )

    def serialize_value(self, value: Any) -> Any:
        if self._serializer is not None:
            return self._serializer(self, value)
        return value

    def _set_field_name(self, name: str) -> None:
        self._name = name
        if self._query_name is UNSET:
            self._query_name = name
        if self._mutate_name is UNSET:
            self._mutate_name = name

    def _set_field_type(self, type_: type) -> None:
        self._analyze_type(type_)

    def __str__(self) -> str:
        return self._name

    def _analyze_type(self, type_: type) -> None:
        from .type import Type
        self._type = None

        if type(type_) not in TypesWithArgs:
            self._type = type_
            return
        
        origin = get_origin(type_)

        if origin is Type:
            self._type = get_args(type_)[0]
        elif issubclass(origin, IterableInterface):
            self._iterable = True
            self._type = get_args(type_)[0]
        elif origin is dict:
            self._allow_raw_dict = True
            self._type = get_args(type_)[1]

        

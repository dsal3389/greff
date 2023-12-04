from __future__ import annotations
from collections.abc import Iterable
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
        self._referenced_graphql_type = None
        self._serializer = serializer

        self._iterable = False
        self._allow_raw_dict = False

    @property
    def name(self) -> str | UnsetType:
        return self._name
    
    @property
    def query_name(self) -> str:
        return self._query_name
    
    @property
    def mutate_name(self) -> str:
        return self._mutate_name

    @property
    def referenced_graphql_type(self) -> Type | None:
        return self._referenced_graphql_type
    
    @property
    def iterable(self) -> bool:
        return self._iterable
    
    def get_default(self) -> Any:
        return self.default

    def validate_value(self, graphlq_type: type[Type], value: Any) -> bool:
        if not isinstance(value, Iterable) and self._iterable:
            raise TypeError(
                f"`{graphlq_type.__name__}.{self.name}` should be a list of graphql types, but graphql returned type `{type(value).__name__}`"
            )
        elif isinstance(value, dict) and (not self._allow_raw_dict and not self._referenced_graphql_type):
            raise TypeError(
                f"`{graphlq_type.__name__}.{self.name}` is a dict, but field does not accept dict nor doesn't reference any sub graphql field"
            )

    def _set_field_name(self, name: str) -> None:
        self._name = name
        if self._query_name is UNSET:
            self._query_name = name
        if self._mutate_name is UNSET:
            self._mutate_name = name

    def _set_field_type(self, type_: type) -> None:
        self._analyze_type(type_)

    def serialize_value(self, value: Any) -> Any:
        if self._serializer is not None:
            return self._serializer(self, value)
        return value

    def __str__(self) -> str:
        return self._name

    def _analyze_type(self, type_: type, _issubtype: bool = False) -> None:
        from .type import Type

        if type(type_) not in TypesWithArgs:
            if issubclass(type_, Type):
                self._referenced_graphql_type = type_
            self._type = None
            return
        
        origin = get_origin(type_)

        if origin is Type:
            self._referenced_graphql_type = get_args(type_)[0]
            self._type = None

        if _issubtype:
            return

        if isinstance(origin, Iterable):
            self._iterable = True
            self._type = get_args(type_)[0]
        elif origin is dict:
            self._allow_raw_dict = True
            self._type = get_args(type_)[1]
        
        if not _issubtype and self._type:
            _analyze_type(self._type, _issubtype=True)
       

        

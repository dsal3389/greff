from __future__ import annotations
from typing import TYPE_CHECKING, Generic, TypeVar

from .field import Field
from .typing import is_classvar


T = TypeVar("T")


def _process_type_cls(cls: type[Type]) -> None:
    cls.__implements__ = dict()

    # if current `Type` is inheriting from another `Type`
    # then its a graphql implementation
    for parent in cls.__mro__[1:]:
        if parent not in (Type, object) and issubclass(parent, Type):
            parent.__implements__[cls.__name__] = cls

    for field_name, field_type in cls.__annotations__.items():
        if field_name.startswith("__") or is_classvar(field_type):
            continue

        field_value = getattr(cls, field_name, None)

        if not isinstance(field_value, Field):
            field_class = Field(field_type, field_name, default=field_value)
            cls.__fields__[field_name] = field_class
            setattr(cls, field_name, field_class)
        else:
            pass


class _GreffTypeMedataClass(type):
    registered_types = {}

    def __new__(cls, name: str, bases: tuple[type], attrs: dict) -> type:
        graphql_type = super().__new__(cls, name, bases, attrs)
        cls.registered_types[name] = graphql_type
        return graphql_type


class Type(Generic[T], metaclass=_GreffTypeMedataClass):
    __queryname__: str = ""
    __implements__: dict[str, type[Type]] = {}
    __fields__: dict[Field] = {}

    def __init__(self, **fields) -> None:
        self._fields = fields

    def __init_subclass__(cls) -> None:
        _process_type_cls(cls)


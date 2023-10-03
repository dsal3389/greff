from __future__ import annotations
from typing import TYPE_CHECKING, Generic, TypeVar

from .field import Field
from .typing import is_classvar


T = TypeVar("T")


def _process_type_metadata(cls: type[Type], query_name: str) -> type[Type]:
    if not query_name:
        cls.__queryname__ = cls.__name__
    else:
        cls.__queryname__ = query_name
    return cls


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


class _CherryPlateTypeMedataClass(type):
    registered_types = {}

    def __new__(cls, name: str, bases: tuple[type], attrs: dict) -> type:
        cherryplate_type = super().__new__(cls, name, bases, attrs)
        cls.registered_types[name] = cherryplate_type
        return cherryplate_type


class Type(Generic[T], metaclass=_CherryPlateTypeMedataClass):
    __queryname__: str = ""
    __implements__: dict[str, type[Type]] = {}
    __fields__: dict[Field] = {}

    def __init__(self, **fields) -> None:
        self._fields = fields

    def __init_subclass__(cls) -> None:
        _process_type_cls(cls)

    def __new__(cls, *args, **kwargs) -> Type:
        # the `__typename` is usually entered when we create that `Type`
        # instance with `Query`, this help us return the correct class instance
        # if it implement multiple different classes
        __typename = kwargs.pop("__typename", None)

        if __typename is not None:
            implemented_type = cls.__implements__.get(__typename)

            if implemented_type is not None:
                return object.__new__(implemented_type)
        return object.__new__(cls)


def type_metadata(
    cls: type[Type] | None = None,
    /,
    query_name: str | None = "",
) -> type[Type]:
    def _type_metadata(cls: type[Type]) -> cls:
        return _process_type_metadata(cls, query_name=query_name)

    if cls is not None:
        return _type_metadata(cls)
    return _type_metadata

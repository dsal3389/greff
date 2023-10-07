from __future__ import annotations
from typing import (
    TYPE_CHECKING,
    Generic,
    TypeVar,
    Any,
    dataclass_transform,
    no_type_check,
    ClassVar,
)
from .types import UNSET
from .field import Field
from .typing import is_classvar


T = TypeVar("T")


object_getattr = object.__getattribute__
object_setattr = object.__setattr__


def _process_graphql_fields(type_: Type, fields: dict[str, Any]):
    fields_copy = fields.copy()
    for field in type_.__fields__.values():
        if field.name not in fields:
            fields_copy[field.name] = field.get_default()
    return fields_copy


@dataclass_transform(
    eq_default=False,
    order_default=False,
    kw_only_default=True,
    field_specifiers=(Field,),
)
class GreffTypeMedataClass(type):
    registered_types = {}

    @no_type_check
    def __new__(cls, name: str, bases: tuple[type], attrs: dict) -> type:
        # if `__typename__` should not inherit parents values, and if its not overwritten
        # or does not exists in new type, then we should provide a default
        if "__typename__" not in attrs:
            attrs["__typename__"] = name.title()

        attrs.update({"__implements__": {}, "__fields__": {}})

        attrs_fields = attrs["__fields__"]

        for field_name, field_type in attrs.get("__annotations__", {}).items():
            if field_name.startswith("__") or is_classvar(field_type):
                continue

            field_value = attrs.get(field_name, UNSET)

            if isinstance(field_value, Field):
                field_class = field_value
                field_class._name = field_name
                field_class.set_field_type(field_type)
            else:
                field_class = Field(field_type, field_name, default=field_value)
            attrs_fields[field_name] = field_class
            attrs[field_name] = field_class

        graphql_type = super().__new__(cls, name, bases, attrs)

        for base in bases:
            # all base classes that are valid graphql types
            # we should put the newly created class as a class they (the bases) implement
            if type(base) is cls:
                base.__implements__[graphql_type.__typename__] = graphql_type

        cls.registered_types[name] = graphql_type
        return graphql_type


class Type(Generic[T], metaclass=GreffTypeMedataClass):
    if TYPE_CHECKING:
        __implements__: ClassVar[dict[str, type[GreffTypeMedataClass]]] = {}
        __mutatename__: ClassVar[str] = ""
        __queryname__: ClassVar[str] = ""
        __typename__: ClassVar[str] = ""
        __fields__: ClassVar[dict[str, Field]] = {}

    __slots__ = ("__dict__",)

    def __init__(self, **fields) -> None:
        processed_fields = _process_graphql_fields(self.__class__, fields)

        # setting the `__dict__` value manually allows us to not
        # overwrite the `__getattribute__` and better performance I guess
        object_setattr(self, "__dict__", processed_fields)

    @no_type_check
    def __setattr__(self, name: str, value: Any) -> None:
        pass

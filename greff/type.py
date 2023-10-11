from __future__ import annotations
from typing import (
    TYPE_CHECKING,
    Generic,
    TypeVar,
    Any,
    ClassVar,
    no_type_check,
)
from typing_extensions import dataclass_transform

from .types import UNSET
from .field import Field
from .typing import is_classvar
from .functions import implement_graphql_type_factory
from .registery import type_registery
from .exceptions import TypenameConflictException


T = TypeVar("T")


object_getattr = object.__getattribute__
object_setattr = object.__setattr__


def _process_graphql_fields(type_: type[Type], fields: dict[str, T]) -> dict[str, T]:
    fields_copy = fields.copy()
    
    for field in type_.__fields__.values():
        field_value = fields.get(field.name, UNSET)

        if field_value is UNSET:
            fields_copy[field.name] = field.get_default()
        elif field.is_graphql_reference:
            if not isinstance(field_value, dict):
                raise TypeError(
                    f"`{type_.__name__}.{field.name}` takes a graphql type, exepected dict value but got `{type(field_value)}`"
                )
            # if the field should be a sub graphlq type field, then
            # it should be a dict with the `__typename`, and we should create the correct
            # type with respect to the `__typename`
            __typename = field_value.pop("__typename", None)
            fields_copy[field.name] = implement_graphql_type_factory(
                field.referenced_graphql_type,
                __typename=__typename,
                **field_value
            )
        else:
            fields_copy[field.name] = field_value
    return fields_copy


@dataclass_transform(
    eq_default=False,
    order_default=False,
    kw_only_default=True,
    field_specifiers=(Field,),
)
class GreffTypeMedataClass(type):
    queryable_registered_types = {}

    @no_type_check
    def __new__(cls, name: str, bases: tuple[type], attrs: dict) -> type:
        __fields__ = attrs.get("__fields__", {})

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
            __fields__[field_name] = field_class

        new_attrs = {
            "__implements__": {},
            # if `__typename__` should not inherit parents values, and if its not overwritten
            # or does not exists in new type, then we should provide a default
            "__typename__": attrs.get("__typename__", name.title()),
            "__fields__": __fields__,
            **__fields__,
            **attrs, 
        }

        graphql_type = super().__new__(cls, name, bases, new_attrs)

        for base in bases:
            # all base classes that are valid graphql types
            # we should put the newly created class as a class they (the bases) implement
            if type(base) is cls:
                base.__implements__[graphql_type.__typename__] = graphql_type
        type_registery.add_type(graphql_type)
        return graphql_type


class Type(Generic[T], metaclass=GreffTypeMedataClass):
    if TYPE_CHECKING:
        __implements__: ClassVar[dict[str, type[GreffTypeMedataClass]]]
        __mutatename__: ClassVar[str]
        __queryname__: ClassVar[str]
        __typename__: ClassVar[str]
        __fields__: ClassVar[dict[str, Field]]
        __mutated_fields__: ClassVar[set[str]]

    __slots__ = ("__dict__", "__mutated_fields__")
    __doc__ = ""

    def __init__(self, **fields) -> None:
        processed_fields = _process_graphql_fields(self.__class__, fields)

        # setting the `__dict__` value manually allows us to not
        # overwrite the `__getattribute__` and better performance I guess
        object_setattr(self, "__dict__", processed_fields)

        # set of field names that were manupulated since 
        # object initilzation will be stored there
        object_setattr(self, "__mutated_fields__", set())

    @no_type_check
    def __setattr__(self, name: str, value: Any) -> None:
        field = self.__fields__.get(name)

        if field is None:
            raise AttributeError( f"unknown attribute `{self.__class__.__name__}.{name}`")
        self.__mutated_fields__.add(name)
        object_setattr(self, name, value)

    def __repr__(self) -> str:
        fields = ", ".join(f"{k}={v}" for k,v in self.__dict__.items())
        return f"{self.__class__.__name__}({fields})"

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
from collections import defaultdict

from .types import UNSET
from .field import Field
from .typing import is_classvar
from .functions import implement_graphql_type_factory
from .registery import type_registery
from .exceptions import TypenameConflictException


T = TypeVar("T")


object_getattr = object.__getattribute__
object_setattr = object.__setattr__


def _process_graphql_fields(type_: type[Type], fields_value: dict[str, T]) -> dict[str, T]:
    fields_value_copy = fields_value.copy()
    
    for field in type_.__fields__.values():
        field_value = fields_value.get(field.name, UNSET)

        if field_value is UNSET:
            fields_value_copy[field.name] = field.get_default()
        elif field.referenced_graphql_type is not None:
            if field.iterable:
                if not isinstance(field_value, (list, tuple, set)):
                    raise TypeError(
                        f"`{type_.__name__}.{field.name}` should be a list of graphql types, but graphql returned type `{type(field_value).__name__}`"
                    )
            elif not isinstance(field_value, dict):
                raise TypeError(
                    f"`{type_.__name__}.{field.name}` takes a graphql type, exepected dict, but graphql returned `{type(field_value).__name__}`"
                )

            def _implement_instance(attrs):
                # if the field should be a sub graphlq type field, then
                # it should be a dict with the `__typename`, and we should create the correct
                # type with respect to the `__typename`
                __typename = attrs.pop("__typename", None)
                return implement_graphql_type_factory(
                    field.referenced_graphql_type, 
                    __typename=__typename, 
                    **attrs
                )
                
            if field.iterable:
                fields_value_copy[field.name] = []

                for attrs in field_value:
                    fields_value_copy[field.name].append(_implement_instance(attrs))
            else:
                fields_value_copy[field.name] = _implement_instance(field_value)
        else:
            fields_value_copy[field.name] = field_value
    return fields_value_copy


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

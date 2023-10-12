from __future__ import annotations
from typing import (
    get_origin,
    get_args,
    ForwardRef,
    _GenericAlias,
    GenericAlias,
    Generic,
)
from .registery import type_registery


TypesWithArgs = (_GenericAlias, GenericAlias, Generic)


def is_classvar(ann: type | None) -> bool:
    return ann and getattr(ann, "_name", None) == "ClassVar"


def is_graphql_type(ann: type | None) -> None:
    from .type import Type
    return ann and issubclass(ann, Type) or get_origin(ann) is Type


def get_grahpql_ref(type_: type) -> type[Type] | None:
    """returns the found graphql reference from given `type_`"""
    from .type import Type

    if type(type_) not in TypesWithArgs:
        if issubclass(type_, Type):
            return type_
        return None

    if get_origin(type_) is not Type:
        return None

    args = get_args(type_)

    if args:
        first_arg = args[0]
        if isinstance(first_arg, ForwardRef):
            return type_registery.get_type(first_arg.__forward_arg__)
        if issubclass(first_arg, Type):
            return first_arg

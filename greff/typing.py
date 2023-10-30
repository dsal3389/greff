from __future__ import annotations
from typing import (
    get_origin,
    get_args,
    ForwardRef,
    _GenericAlias,
    GenericAlias,
    Generic,
    Union
)
from .registery import type_registery


TypesWithArgs = (_GenericAlias, GenericAlias, Generic)


def is_classvar(ann: type | None) -> bool:
    return ann and getattr(ann, "_name", None) == "ClassVar"


def is_graphql_type(ann: type | None) -> None:
    from .type import Type
    return ann and issubclass(ann, Type) or get_origin(ann) is Type


def is_union(anno: type | None) -> bool:
    return get_origin(anno) is Union

from __future__ import annotations
from typing import TYPE_CHECKING
from .functions import isqueryable, ismutable

if TYPE_CHECKING:
    from .type import Type


class _TypeRegistery:
    """
    _TypeRegistery:
        should be used as a singleton, this class stores all registered graphql types
        and it orginize them by queryable/mutateable.

        this helps when scalaring graphql dict to python objects, example

        ```
        class Foo(greff.Type):
            __queryname__ = "foos"  # the queryname in graphql, will be registered
            ...

        graphql_response = {
            "books": [...],
            "foos": [...]
        }

        # iter over each key in the response and get the correct type
        for queryname in graphql_response:
            type_ = type_registery.get_queryable(queryname)
        ```
    """
    def __init__(self) -> None:
        self._queryable_types = {}
        self._mutable_types = {}
        self._types = {}

    def add_type(self, type_: type[Type]) -> None:
        if isqueryable(type_):
            self._queryable_types[type_.__queryname__] = type_
        if ismutable(type_):
            self._mutable_types[type_.__mutatename__] = type_
        self._types[type_.__name__] = type_

    def get_type(self, name: str) -> type[Type] | None:
        return self._types.get(name)

    def get_queryable(self, queryname: str) -> type[Type] | None:
        return self._queryable_types.get(queryname)


# singleton root registery
type_registery = _TypeRegistery()

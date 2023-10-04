from __future__ import annotations
import enum
from typing import TYPE_CHECKING, Iterable

from .type import Type
from .field import Field
from .functions import implement_graphql_type_factory

if TYPE_CHECKING:
    from .client import Client


class QueryOP:
    FRAGMENT_REF = enum.auto()
    ARGUMENTS = enum.auto()
    ON = enum.auto()


class Query:
    def __init__(
        self, 
        client: Client | None, 
        query: Iterable[tuple[type[Type], Field, ...]],
        fragments: tuple[str, tuple[...]]
    ) -> None:
        self._client = client
        self._query = query
        self._fragments = fragments

        self._queryname_to_type = self._process_queryname_to_type()
        self._last_response: dict | None = None

    def __iter__(self) -> Iterable[Type]:
        """
        when iterating the query object, it actually sends the request throught the bound
        client and return an instance of the corresponding class which was given in the query
        """
        if self._client is None:
            raise ValueError(
                f"`Query` class has not client bound to it, cannot request data"
            )

        response = self._client.query_request("".join(self.serialize()))
        errros = response.get("errors")

        self._last_response = response

        # TODO: raise graphql exception
        if errros is not None:
            raise Exception(errros)

        for query_name, instance_attrs in response.get("data", {}).items():
            type_ = self._queryname_to_type.get(query_name)

            if type_ is None:
                raise ValueError(
                    f"unknown query name returned `{query_name}`, probably a bug, not sure how we got here..."
                )

            for attrs in instance_attrs:
                __typename = attrs.pop("__typename", "")
                yield implement_graphql_type_factory(type_, __typename=__typename, **attrs)

    def __next__(self) -> Type:
        return next(self.__iter__())

    def serialize(self) -> str:
        """serialize given query to string"""
        if not isinstance(self._query, (list, tuple, set)):
            raise TypeError(
                f"given query data is not any of types `list`, `tuple` or `set`, but of type `{type(self._query)}`"
            )

        yield "query{"
        for type_query in self._query:
            yield from self._serialize_list(type_query)
        yield "}"

    def _serialize_list(self, type_query_list: tuple[Type, tuple[Field | str]]) -> Iterable[str]:
        if len(type_query_list) < 2:
            raise ValueError()

        type_, type_fields = type_query_list

        if not issubclass(type_, Type):
            raise TypeError(f"queried type does not inherit from `greff.Type`")

        yield type_.__queryname__

        buf = "{"
        first = True
        for field in type_fields:
            if first:
                first = False
            else:
                buf = ","

            if isinstance(field, (list, tuple, set)):
                yield buf
                yield from self._serialize_list(field)
            elif isinstance(field, (str, int, Field)):
                yield buf + str(field)
        yield ",__typename}"

    def _process_queryname_to_type(self) -> dict[str, type[Type]]:
        map_ = {}

        for type_, _ in self._query:
            if not issubclass(type_, Type):
                raise TypeError()
            map_[type_.__queryname__] = type_
        return map_

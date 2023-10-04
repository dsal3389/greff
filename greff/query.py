from __future__ import annotations
import enum
from typing import TYPE_CHECKING, Iterable, Any

from .type import Type
from .field import Field
from .functions import implement_graphql_type_factory

if TYPE_CHECKING:
    from .client import Client


class QueryOP(enum.Enum):
    FRAGMENT = enum.auto()
    FRAGMENT_REF = enum.auto()
    ARGUMENT = enum.auto()
    ON = enum.auto()


def argument(type_: type[Type], **arguments) -> tuple[QueryOP, type[Type], dict]:
    return (QueryOP.ARGUMENT, type_, arguments)


def fragment(name: str, *, on: type[Type]) -> tuple[QueryOP, str, type[Type]]:
    return (QueryOP.FRAGMENT, name, on)


def fragment_ref(name: str) -> tuple[QueryOP, str]:
    return (QueryOP.FRAGMENT_REF, name)


class Query:
    def __init__(
        self, 
        client: Client | None, 
        query: Iterable[tuple[type[Type], Field, ...]],
        fragments: dict[tuple, tuple[...]]
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
            yield from self._serialize_type_query(type_query)
        yield "}"

        # iter over each given fragment
        for fragment, fragment_query in self._fragments.items():
            if not isinstance(fragment, (tuple, list, set)) or len(fragment) < 2:
                raise ValueError(
                    f"fragment dict key expected to be a tuple or with length bigger then 2"
                )

            query_op, *v = fragment
            if query_op != QueryOP.FRAGMENT:
                raise ValueError(f"expected `QueryOP.FRAGMENT`, but got {query_op}")
            
            fragment_name, fragment_on_type = v
            yield f"fragment {fragment_name} on {fragment_on_type.__typename__}"
            yield from self._serialize_query_fields(fragment_query)

    def _serialize_type_query(self, type_query_list: tuple[Type, tuple[Field | str]]) -> Iterable[str]:
        if len(type_query_list) < 2:
            raise ValueError()

        type_, type_fields = type_query_list

        if not issubclass(type_, Type):
            raise TypeError(f"queried type does not inherit from `greff.Type`")
            
        yield type_.__queryname__
        yield from self._serialize_query_fields(type_fields)

    def _serialize_query_fields(self, fields: tuple[Field | str]) -> Iterable[str]:
        sep = ","

        yield "{"
        for field in fields:
            if isinstance(field, (list, tuple, set)):
                yield sep
                # iterables may be query operations
                if self._is_query_op(field):
                    yield self._serialize_query_op(field)
                else:
                    yield from self._serialize_query_fields(field)
            elif isinstance(field, (str, int, Field)):
                yield sep + str(field)
        yield ",__typename}"

    def _serialize_query_op(self, op_data: tuple[QueryOP, ...]) -> str:
        if len(op_data) < 2:
            raise ValueError(f"expected from query operation to be a list with len >= 2")
        
        op, *data = op_data
        if op == QueryOP.FRAGMENT_REF:
            return f"... {data[0]}" 
        # testings
        raise Exception() 

    def _is_query_op(self, o: Iterable[Any]) -> bool:
        return len(o) > 1 and o[0] in QueryOP

    def _process_queryname_to_type(self) -> dict[str, type[Type]]:
        map_ = {}

        for type_, _ in self._query:
            if not issubclass(type_, Type):
                raise TypeError()
            map_[type_.__queryname__] = type_
        return map_

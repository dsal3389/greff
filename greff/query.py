from __future__ import annotations
import enum
import itertools
from typing import TYPE_CHECKING, Iterable, Any

from .type import GreffTypeMedataClass, Type
from .field import Field
from .functions import implement_graphql_type_factory
from .registery import type_registery
from .exceptions import (
    InvalidQueryException,
    QueryOperationException, 
    GraphqlResponseException, 
)

if TYPE_CHECKING:
    from .client import Client


class QueryOP(enum.Enum):
    FRAGMENT = enum.auto()
    FRAGMENT_REF = enum.auto()
    ARGUMENT = enum.auto()
    ON = enum.auto()


def on(type_: type[Type] | Field) -> tuple[QueryOP, type[Type]]:
    return (QueryOP.ON, type_)


def argument(
    type_: type[Type] | Field, **arguments
) -> tuple[QueryOP, type[Type], dict]:
    return (QueryOP.ARGUMENT, type_, arguments)


def fragment(name: str, *, on: type[Type] | Field) -> tuple[QueryOP, str, type[Type]]:
    return (QueryOP.FRAGMENT, name, on)


def fragment_ref(name: str) -> tuple[QueryOP, str]:
    return (QueryOP.FRAGMENT_REF, name)


class QueryRequest:
    def __init__(
        self,
        query: Iterable[tuple[type[Type], Field, ...]] | str,
        fragments: dict[tuple, tuple[...]] | None,
    ) -> None:
        self._query = query
        self._fragments = fragments

    def serialize(self) -> str:
        return "".join(itertools.chain(self.serialize_query(), self.serialize_fragments()))

    def serialize_query(self) -> Iterable[str]:
        """serialize given query to string"""
        if isinstance(self._query, str):
            yield self._query
        else:
            if not isinstance(self._query, (list, tuple, set)):
                raise TypeError(
                    f"given query data is not any of types `str`, `list`, `tuple` or `set`, but of type `{type(self._query)}`"
                )

            yield "query{"
            for type_query in self._query:
                yield from self._serialize_type_query(type_query)
            yield "}"

    def serialize_fragments(self) -> Iterable[str]:
        if not self._fragments:
            return

        for fragment, fragment_query in self._fragments.items():
            if not isinstance(fragment, (tuple, list, set)) or len(fragment) < 2:
                raise ValueError(
                    f"fragment dict key expected to be a tuple or with length bigger then 2"
                )

            query_op, *v = fragment
            if query_op != QueryOP.FRAGMENT:
                raise ValueError(f"expected `QueryOP.FRAGMENT`, but got {query_op}")

            fragment_name, fragment_on_type = v
            yield self._serialize_query_op(fragment, allowed_ops=(QueryOP.FRAGMENT,))
            yield from self._serialize_query_fields(fragment_query)

    def _serialize_type_query(
        self,
        type_query_list: tuple[Type, tuple[Field | str]],
        is_subfield: bool = False,
    ) -> Iterable[str]:
        if len(type_query_list) < 2:
            raise InvalidQueryException(
                f"query is not valid, expected a list with first index `Type` and second index list of fields"
            )

        type_field_or_op, type_fields = type_query_list

        if isinstance(type_field_or_op, (tuple, list, set)):
            if not self._is_query_op(type_field_or_op):
                raise ValueError(f"first argument in query should be the graphql type")
            yield self._serialize_query_op(
                type_field_or_op, allowed_ops=(QueryOP.ARGUMENT, QueryOP.ON)
            )
        elif isinstance(type_field_or_op, Field):
            # when the given type is a `Field` we are probably
            # inside a sub field
            if not type_field_or_op.is_graphql_reference:
                raise TypeError(
                    f"given value for subfield `{type_field_or_op.name}` must reference a valid graphql type"
                )
            yield type_field_or_op.__queryname__
        else:
            if is_subfield:
                raise TypeError(
                    f"cannot provide a standalone graphql field as a value to a subfield, given type is `{type_field_or_op}`"
                )
            if not issubclass(type_field_or_op, Type):
                raise TypeError(f"queried type does not inherit from `greff.Type`")
            yield type_field_or_op.__queryname__
        yield from self._serialize_query_fields(type_fields)

    def _serialize_query_fields(self, fields: tuple[Field | str]) -> Iterable[str]:
        first = True
        buf = "{"

        for field in fields:
            if first:
                first = False
            else:
                buf = ","

            if isinstance(field, (list, tuple, set)):
                yield buf
                # iterables may be query operations
                if self._is_query_op(field):
                    yield self._serialize_query_op(field)
                else:
                    # if its a nested field in the fields, it means
                    # its a subfield, and we should serialize it like regular query
                    yield from self._serialize_type_query(field, is_subfield=True)
            elif isinstance(field, (str, int, Field)):
                yield buf + str(field)
        yield ",__typename}"

    def _serialize_query_op(
        self,
        op_data: tuple[QueryOP, ...],
        *,
        allowed_ops: QueryOP | tuple[QueryOP] = QueryOP,
    ) -> str:
        """serializes unique query operations to graphql string"""
        op, *data = op_data
        if not op in allowed_ops:
            raise QueryOperationException(op, allowed_ops)

        if op is QueryOP.ON:
            return f"... on {data[0].__queryname__}"
        if op is QueryOP.FRAGMENT_REF:
            return f"... {data[0]}"
        if op is QueryOP.FRAGMENT:
            fragment_name, fragment_on_type = data
            return f"fragment {fragment_name} on {fragment_on_type.__typename__}"
        if op is QueryOP.ARGUMENT:
            type_, kwargs = data
            serialized_arguments = "".join(f'{k}:"{v}"' for k, v in kwargs.items())
            return f"{type_.__queryname__}({serialized_arguments})"
        # testings
        raise Exception()

    def _is_query_op(self, o: Iterable[Any]) -> bool:
        """returns a boolean value indicating if given iterable is a unique query operation"""
        return len(o) > 1 and o[0] is not type and isinstance(o[0], QueryOP)


class QueryResponse:
    def __init__(self, response: dict[str, Any]) -> None:
        self._response = response

    def __iter__(self) -> Iterable[Type]:
        yield from itertools.chain.from_iterable(self.types())

    @property
    def response(self) -> dict[str, Any]:
        return self._response

    def types(self) -> tuple[Type, ...]:
        iterables = []

        for query_name, instance_attrs in self.response.get("data", {}).items():
            type_ = type_registery.get_queryable(query_name)

            if type_ is None:
                raise ValueError(
                    f"unknown query name returned `{query_name}`, probably a bug, not sure how we got here..."
                )
            iterables.append(self._iter_type(type_, instance_attrs))
        return iterables

    def _iter_type(self, type_: type[Type], instance_attrs: list[dict] | dict) -> Iterable[Type]:
        if isinstance(instance_attrs, list):
            for attrs in instance_attrs:
                # we pop the `__typename` from the data
                # because we don't want to pass it to the instance as argument
                __typename = attrs.pop("__typename", None)
                yield implement_graphql_type_factory(
                    type_, __typename=__typename, **attrs
                )
        else:
            __typename = instance_attrs.pop("__typename", None)
            yield implement_graphql_type_factory(type_, __typename=__typename, **instance_attrs)

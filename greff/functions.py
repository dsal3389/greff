from __future__ import annotations
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from .type import Type


def isqueryable(type_: Type) -> bool:
    return bool(getattr(type_, "__queryname__", None))


def ismutable(type_: Type) -> bool:
    return bool(getattr(type_, "__mutatename__", None))


def implement_graphql_type_factory(
    cls: type, /, *, __typename: str | None = None, **kwargs
) -> Type:
    """returns the correct class implementation base on the given `__typename`"""
    __implements__ = getattr(cls, "__implements__", None)

    if __implements__ is None:
        raise TypeError(
            f"given class to `implement_graphql_type` must have implements, `{cls.__name__}.__implements__`"
        )

    if __typename is not None:
        type_cls = __implements__.get(__typename)
        if type_cls is not None:
            return type_cls(**kwargs)
    return cls(**kwargs)

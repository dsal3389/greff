from .type import Type


def implement_graphql_type_factory(cls: type[Type], /, *, __typename: str = "", **kwargs) -> Type:
    """returns the correct class type base on the given `__typename`"""
    if not issubclass(cls, Type):
        raise TypeError(
            f"given class to `implement_graphql_type` does not inherit from `greff.Type`"
        )

    type_cls = cls.__implements__.get(__typename)
    
    if type_cls is not None:
        return type_cls(**kwargs)
    return cls(**kwargs)

from typing import get_origin


def is_classvar(ann: type | None) -> bool:
    return ann and getattr(ann, "_name", None) == "ClassVar"

from typing import Any
class Foo(object):
    def __getattr__(self, name: str) -> Any | None: ... # incomplete
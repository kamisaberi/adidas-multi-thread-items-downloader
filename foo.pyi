from typing import Any
class Foo(object):
    def __init__(self , first_name : str = "" ,last_name:str = "" , age : int = 0 )->None:...
    def __getattr__(self, name: str) -> Any | None: ... # incomplete

    @property
    def first_name(self)->str:...

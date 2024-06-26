from typing import Any


class ItemInfo:
    order: int = ...
    done: bool = ...
    total_reviews_count: int = ...
    downloaded_reviews_count: int = ...
    media_links: list[str] = ...
    media_done: bool = ...

    def __init__(self, order: int = 1, done: bool = False, total_reviews_count: int = -1,
                 downloaded_reviews_count: int = 0, media_links: list[str] = [], media_done: bool = False) -> None: ...

    # self.reviews_done: bool

    def __getattr__(self, name: str) -> Any | None: ...  # incomplete
# @property
# def reviews_done(self) -> bool: ...

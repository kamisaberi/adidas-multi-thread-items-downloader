import threading

import enum


class Adidas(threading.Thread):
    """
        Instance Members:
            thread_id: int = 0
            thread_type: TYPES = TYPES.NONE
            products_data: list[dict] = []
            item_start = 0
            item_end = 0
        Static Members :
            items: list[dict] = []
            model_product_objects: list[tuple[str, str]] = list()
            next_start_point:
            settings_file_path:
            product_file_name_prefix:
            product_files_path:
            gotten_items_list:
            params:
            headers:
            items_url:
            reviews_url:
            items_per_page:
            items_count:
            start_from:
            reminder_from_last_check:
            items_threads_count:
            reviews_threads_count:
    """

    threads = None
    items_should_update: threading.Event = ...
    thread_type = ...
    items_count = ...
    items = ...
    items_info = ...
    items_per_page = ...
    next_start_point: int = ...

    class Settings:
        @staticmethod
        def load_settings(): ...

    def __init__(self, thread_id, thread_type: TYPES, group=None, target=None, name=None, args=(), kwargs=None, *,
                 daemon=None): ...

    @staticmethod
    def _replace_bulk_using_data(item_start, items): ...


class TYPES(enum.Enum):
    NONE = ...
    CHECK_PREFERENCES = ...
    GET_ITEMS_LIST = ...
    GET_REVIEWS = ...
    DOWNLOAD_PRODUCT_MEDIA = ...

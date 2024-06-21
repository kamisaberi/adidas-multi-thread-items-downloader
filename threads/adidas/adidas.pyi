class Adidas:
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

    thread_type = ...
    items_count = ...
    items = ...
    items_info = ...
    events = ...
    items_per_page = ...
    next_start_point: int = ...
    Settings = ...

    def __init__(self):...

    @staticmethod
    def update_items_info(item_start, items):...



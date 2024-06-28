from typing import NamedTuple, Any

URLS = NamedTuple("urls", [("items", str), ("reviews", str)])(
    "https://www.adidas.at/api/plp/content-engine/search?",
    "https://www.adidas.at/api/models/{model_id}/reviews?bazaarVoiceLocale=de_AT&feature&includeLocales=de%2A&limit={limit}&offset={offset}&sort=newest"
)
PATHS = NamedTuple("paths",
                   [("settings_file_path", str), ("product_file_name_prefix", str), ("product_files_path", str)])(
    "prefs/settings.json", "pr-", "files")
TEMPLATES = NamedTuple("templates", [("params", dict[str:Any]), ("headers", dict[str:Any])])(
    {"query": "all", "start": 0, "sort": "newest-to-oldest"},
    {"authority": "www.adidas.at", "accept": "*/*", "accept-language": "en-US,en;q=0.9,fa;q=0.8",
     "content-type": "application/json", "user-agent": "PostmanRuntime/7.35.0"})

SORT_NEWEST = "newest-to-oldest"
SORT_TOP_SELLERS = "top-sellers"

CHECK_PREFERENCES_INTERVAL = 60  # in seconds
CHECK_NEW_REVIEWS_INTERVAL = 60  # in seconds
INITIAL_CHECK_PREFERENCES_DELAY = 2  # in seconds

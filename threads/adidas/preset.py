from collections import namedtuple

URLS = namedtuple("urls", ["items", "reviews"])(
    "https://www.adidas.at/api/plp/content-engine/search?",
    "https://www.adidas.at/api/models/{model_id}/reviews?bazaarVoiceLocale=de_AT&feature&includeLocales=de%2A&limit={limit}&offset={offset}&sort=newest"
)
PATHS = namedtuple("paths", ["settings_file_path", "product_file_name_prefix", "product_files_path"])(
    "prefs/settings.json", "pr-", "files")
TEMPLATES = namedtuple("templates", ["params", "headers"])(
    {"query": "all", "start": 0, "sort": "newest-to-oldest"},
    {"authority": "www.adidas.at", "accept": "*/*", "accept-language": "en-US,en;q=0.9,fa;q=0.8",
     "content-type": "application/json", "user-agent": "PostmanRuntime/7.35.0"}
)

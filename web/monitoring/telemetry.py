from prometheus_client import Counter, Gauge

REQUEST_COUNTER = Counter(
    "app_num_requests",
    "Total number of requests received",
    ["endpoint", "method"],
)

MEM_GAUGE = Gauge(
    "app_current_memory",
    "Total RAM consumed by application",
)

UPTIME_GAUGE = Gauge(
    "app_uptime",
    "Uptime of the application",
)

SEARCH_CACHE_HITS_GAUGE = Gauge(
    "app_search_cache_hits",
    "Total hits from search cache",
)
SEARCH_CACHE_MISSES_GAUGE = Gauge(
    "app_search_cache_misses",
    "Total misses from search cache",
)

INDEX_CACHE_HITS_GAUGE = Gauge(
    "app_index_cache_hits",
    "Total hits from index cache",
)
INDEX_CACHE_MISSES_GAUGE = Gauge(
    "app_index_cache_misses",
    "Total misses from index cache",
)

AUTOCOMPLETE_CACHE_HITS_GAUGE = Gauge(
    "app_autocomplete_cache_hits",
    "Total hits from autocomplete cache",
)
AUTOCOMPLETE_CACHE_MISSES_GAUGE = Gauge(
    "app_autocomplete_cache_misses",
    "Total misses from autocomplete cache",
)

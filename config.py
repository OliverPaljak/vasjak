# DATA ABOUT STORES (do not change them, unless you know what you are doing) -#
STORES_DATA = {
    "rimi": {
        "max_page_size": 80,
        "min_page_size": 1,
        "base_url":  "https://www.rimi.ee/epood/ee/otsing?page={page_nr}&pageSize={page_size}&query={query}:{sort}",
        "query_sort_values": {
            "default": "relevance",
            "asc": "price-asc",
            "desc": "price-desc",
            "asc_per": "priceunit-asc",
            "desc_per": "priceunit-desc"
        }
    },
    "selver": {
        "max_page_size": 96,
        "min_page_size": 24,
        "base_url": "https://www.selver.ee/catalogsearch/result/index/?dir={_dir}&limit={page_size}&order={sort}&p={page_nr}&q={query}",
        "query_sort_values": {
            "default": {"_dir": "asc", "sort": "relevance"},
            "asc": {"_dir": "asc", "sort": "price"},
            "desc": {"_dir": "desc", "sort": "price"},
            # asc_per and desc_per are not supported by selver - fallback to
            # default mode
            "asc_per": {"_dir": "asc", "sort": "relevance"},
            "desc_per": {"_dir": "asc", "sort": "relevance"}
         }
     }
}

# OPTIONS (change them to your liking) ---------------------------------------#
DEFAULT_OPTIONS = {
    "product_limit": 20,

    "query_limit": 100,
    "query_sort": "default",
    
    "search_precise": True,
    "search_strict": False,

    "glue_duplicates": False,
    
    "sort_desc": False,
    "sort_price_per": False,

    "silent_mode": False,
    "human_read": True,
    "out_str":"{store_name:<10}{product_name:<50}{price:<10}{price_per:<20}\n",

    "cache_file": "cache.json",
    "cache_time": 60 * 60 * 12, #in seconds

    "search_term_dicts": {}
}

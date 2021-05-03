"""
Module for managing cache.

NOTE: The cache consists of only parsed products that were recieved from the
parsers based on the query. No end (filtered, sorted, limited) result is
cached as filtering, sorting and limiting is very quick and cheap compared to
making requests and parsing the products. This also enables the user make only
one (big) request and play with the filtering options without the need to wait
for the requests to made and parsing to complete.

All constants (such as DEFAULT_OPTIONS) can be found in config.py
"""

# IMPORTS --------------------------------------------------------------------#
# Native imports
import os
import time
import json

# Project imports
from config import *
import rimi_parser as rimi
import selver_parser as selver

# GLOBAL VARIABLES -----------------------------------------------------------#
# Parser list for calling out parser by store name
stores = {
    "rimi": rimi,
    "selver": selver
}

# The cache variable (this is were all the cache is stored and read from)
cache = {}

# Has the cache been modified
cache_modified = False

# PRIVATE FUNCTIONS ----------------------------------------------------------#
def _term_to_key(term_dict, query_limit=DEFAULT_OPTIONS["query_limit"],
                 query_sort=DEFAULT_OPTIONS["query_sort"]):
    """
    Generate cache key based on the search parameters. The key relies on the
    search term that the query was based on, on the query limit and on the
    query sort method - basically if the request parameters are changed, then
    it automatically means a new cache field.
    
    Paramters
    ---------
    term_dict : dictionary
        The dictionary that contains the search term (i.e. the string that the
        query was based on) for making the key. The stucture of the dictionary
        should be the following:
        {
            "search_term": <value>,
            "add_terms": [<value_1>, <value_2>]
        }
    query_limit : int
        The maximum amount of products that the user requested. Optional, see
        DEFAULT_OPTIONS dictionary in config.py for default value.
    query_sort : str (default|asc|desc|asc_per|desc_per)
        The sort method that was used in the request.

    Returns
    -------
    str
        The generated cache key
    """
    options_str = term_dict["search_term"] +\
                  "+query_limit=" + str(query_limit) +\
                  "+query_sort=" + str(query_sort)
    return options_str

# PUBLIC FUNCTIONS -----------------------------------------------------------#
def write_to_file(file_name=DEFAULT_OPTIONS["cache_file"],
                  cache_time=DEFAULT_OPTIONS["cache_time"],
                  silent_mode=DEFAULT_OPTIONS["silent_mode"]):
    """
    Write the cache (variable contents) to the cache file.

    Parameters
    ----------
    file_name : str
        The cache file name/path. Optional, see DEFAULT_OPTIONS dictionary in
        config.py for default value.
    cache_time : int
        The cache keep-alive time. Optional, see DEFAULT_OPTIONS dictionary in
        config.py for default value. NOTE: if cache_time is 0 or negative then
        cache is disabled - that means no reading/writing from the cache file
        is taken place. To see more details on the cache, see the get function
        in this module.
    silent_mode : bool
        If silent mode is not used (silent_mode=False), then the program tries
        to tell user what it is doing. If it is used (silent_mode=True), then
        user notification is kept at bare minimum. Optional, see
        DEFAULT_OPTIONS dictionary in config.py for default value. 
    """

    if cache_time < 1:
        return
    
    if not silent_mode:
        print("\n==cacher")
        print("Trying to write cache to file \"" + file_name + "\"")
    
    global cache, cache_modified
    
    if not cache_modified and not silent_mode:
        print("Cache has been not modified!")
        print("No need to write to cache file!")
        return

    cache_json = json.dumps(cache, indent=4)
    cache_file = open(file_name, "w")

    try:
        cache_file.write(cache_json)
    except:
        cache_file.close()
        if not silent_mode:
            print("ERROR: Failed to write the cache to the file \"" + \
                   file_name + "\"!")
            print("Cache writing failed!")
        return
    
    cache_file.close()
    if not silent_mode:
        print("Cache write to file \"" + file_name + "\" was successful!")



def read_from_file(file_name=DEFAULT_OPTIONS["cache_file"],
                   cache_time=DEFAULT_OPTIONS["cache_time"],
                   silent_mode=DEFAULT_OPTIONS["silent_mode"]):
    """
    Read cache from the cache file.
    
    Parameters
    ----------
    file_name : str
        The cache file name/path. Optional, see DEFAULT_OPTIONS dictionary in
        config.py for default value.
    cache_time : int
        The cache keep-alive time. Optional, see DEFAULT_OPTIONS dictionary in
        config.py for default value. NOTE: if cache_time is 0 or negative then
        cache is disabled - that means no reading/writing from the cache file
        is taken place. To see more details on the cache, see the get function
        in this module.
    silent_mode : bool
        If silent mode is not used (silent_mode=False), then the program tries
        to tell user what it is doing. If it is used (silent_mode=True), then
        user notification is kept at bare minimum. Optional, see
        DEFAULT_OPTIONS dictionary in config.py for default value. 

    Returns
    -------
    Does not return anything but if reading is successful, then the cache has
    been read to the global variable/dictionary cache.
    """

    if cache_time < 1:
        return
    
    if not silent_mode:
        print("\n==cacher")
        print("Trying to read cache from file \"" + file_name + "\"")

    if not os.path.isfile(file_name):
        if not silent_mode:
            print("ERROR: File \"" + file_name + "\" not found!")
            print("Cache reading failed!")
        return

    if not os.access(file_name, os.R_OK):
        if not silent_mode:
            print("ERROR: File \"" + file_name + "\" not readable!")
            print("Cache reading failed!")
        return

    modified_time = round(os.path.getmtime(file_name))
    now = round(time.time())

    if now > (modified_time+cache_time):
        if not silent_mode:
            print("Cache is expired!")
            print("Cache reading failed!")
        return
    
    cache_file = open(file_name, "r")
    try:
        global cache
        cache = json.load(cache_file)
    except ValueError:
        cache = {}
        cache_file.close()
        if not silent_mode:
            print("ERROR: Failed to parse the cache json!")
            print("Cache reading failed!")
        return

    cache_file.close()
    if not silent_mode:
        print("Cache read from file \"" + file_name + "\" was successful!")

def get(term_dict, store, options=DEFAULT_OPTIONS):
    """
    Function for getting parsed products through cache. If the requested
    products are in the cache variable/dictionary, then the cached values will
    be returned. Otherwise, if the requested products are not in the cache,
    then the cacher will return the parsers' (e.g. rimi_parser.py and
    selver_parser.py) values.

    NOTE: Downloading the HTMLs and parsing them (i.e. using the parsers) is
    pretty slow.

    NOTE: It is possible to disable cache by setting the cache_time option
    to 0 or negative in the options directory - this will ensure that no
    reading and writing from/to the cache file will take place (every time the
    program is run the HTML downloading and parsing will also take place).
    However, this does not disable the use of the cache variable as it is
    possible to request the same search term (which the download query is based
    on and thus also the parsing) with different additional search terms (which
    are used for filtering the products in the filterer after parsing has taken
    place) - all that means that we can/should reduce the amount of the HTML
    downloads and use already downloaded and parsed set of the same products
    for filtering with the additional terms.
    
    Parameters
    ----------
    term_dict : dictionary
        The dictionary that contains the search term (i.e. the string that the
        download request is based on) and also additional search term for
        filtering out the products later. The stucture of the dictionary should
        be the following:
        {
            "search_term": <value>,
            "add_terms": [<value_1>, <value_2>]
        }
    store : str
        The store name/key value for knowing what parser to use. See the stores
        dictionary at the top of this module.
    options : dictionary
        The dictionary that contains the user specified options (usually from
        the command line interface - see cli.py). Used to change how the
        program operates. Optional, see DEFAULT_OPTIONS dictionary in config.py
        for default values.

    Returns
    -------
    list
        The parsed (unfiltered) products as dictionaries (either from cache or
        directly from the parsers)
    """
    cache_key = _term_to_key(term_dict, options["query_limit"],
                             options["query_sort"])
    
    global cache, cache_modified
    if store not in cache:
        cache[store] = {}

    if cache_key not in cache[store]:
        if not options["silent_mode"]:
            print("\n==cacher::" + store)
            print("Cache not found for current search conditions!")
            print("We will have to download the products live!")

        cache[store][cache_key] = stores[store].get(term_dict, options)
        cache_modified = True
    elif not options["silent_mode"]:
        print("\n==cacher::" + store)
        print("Cache found for current search conditions!")
        print("Will return the cached results!")
    
    return cache[store][cache_key]

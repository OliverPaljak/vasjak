"""
Module for getting the HTMLs from the e-stores

Depends on the request library (should be installed by the user)
"""


# IMPORTS --------------------------------------------------------------------#
# Native imports
import math
from urllib.parse import quote

# Library imports
import requests

# Project imports
from config import *

# PUBLIC FUNCTIONS -----------------------------------------------------------#
def download(term_item, store, url_format_cb, is_last_page_cb,
             query_limit=DEFAULT_OPTIONS["query_limit"],
             query_sort=DEFAULT_OPTIONS["query_sort"],
             silent_mode=DEFAULT_OPTIONS["silent_mode"]):
    """
    Get HTMLs from the selected store based on the user query.

    Parameters
    ----------
    term_item : dictionary
        The dictionary that contains the search term (the string that the
        query was based on) and additional search term for filtering out the
        product during the filtering process. If the search term string is
        empty, then the function will not download anything (returns empty
        list)
    store : str
        The store name in the STORES_DATA dictionary (see config.py). If the
        provided store name is not found in the dictionary, the function will
        not download anything (returns empty list)
    url_format_cb : callback
        Callback that takes the base url as an argument and formats it for the
        given store. The callback should return a (formatted) string.
    is_last_page_cb : callback
        Callback that takes raw HTML as a parameter and checks if the provided
        HTML is the last page (i.e. it has no products in it). Should return
        True or False
    query_limit : int
        The maximum amount of products that the user wants to request from the
        e-store
    query_sort : str (default|asc|desc|asc_per|desc_per)
        Let the e-store sort the products when making the request.
        Possible values:
            default - do not sort at all/use the e-store's default way of
                      sorting (this usually means by relevance or by
                      popularity). Gives the most accurate results.
            asc - sort ascendigly
            desc - sort descendingly
            asc_per - sort ascendingly but use the price per kg/l/etc
            desc_per - sort descendingly but use the price per kg/l/etc

        NOTE: Using any other values than "default" will probably not give very
        accurate results corresponding to the search term and also all the
        available values (especially asc_per and desc_per) are not supported by
        all the e-stores.
    
        Rimi e-store supports all the query_sort values.
        Selver e-store supports default, asc and desc query sort methods.

        NOTE: If e-store does not support one of the sorting values but it is
        requested by the user, then the request will be made using the default
        sorting option.
    silent_mode : bool
        If silent mode is not used (silent_mode=False), then the program tries
        to tell user what it is doing. If it is used (silent_mode=True), then
        user notification is kept at bare minimum. Optional, see
        DEFAULT_OPTIONS dictionary in config.py for default value. 

    Returns
    -------
    list
        List of the recieved products pages htmls
    """

    if term_item["search_term"] == "" or store not in STORES_DATA:
        return []

    htmls = []
    
    max_page_size = STORES_DATA[store]["max_page_size"]
    min_page_size = STORES_DATA[store]["min_page_size"]

    if query_limit < min_page_size:
        query_limit = min_page_size
    
    # If the amount of requested products is equal or smaller than the e-store
    # can fit on a single page, then only request the one page and return
    # that html (altough function still returns a list but that list is only
    # one element long)
    if query_limit <= max_page_size:
        request_url = url_format_cb(term_item["search_term"], 1, query_limit,
                                    query_sort)
        
        if not silent_mode:
            print("We need to download 1 page")
            print("Downloading HTML...")
            print(request_url)
        
        htmls.append(requests.get(request_url).content.decode("utf-8"))

        return htmls
    
    
    # If the amount of requested prodcuts is bigger than the e-store can fit
    # on a single page, then we must request as much pages as necessary (that
    # means that we need to fetch so many pages that could return the amount
    # of the requested products)

    # Calculate how many pages we should request
    page_count = math.ceil(query_limit / max_page_size);

    if not silent_mode:
        print("We need to download at maximum " + str(page_count) + " pages")
        print("This will probably take a while...")

    # Calculate how many products are there on the last page
    last_page_limit = query_limit % max_page_size;
    if last_page_limit > 0 and last_page_limit < min_page_size:
        last_page_limit = min_page_size

    # Set the query limit to maximum page size
    query_limit = max_page_size;
    
    for i in range(page_count):
        if i+1 == page_count and last_page_limit > 0:
            query_limit = last_page_limit
        
        # Make the request url (see config.py for more details)
        request_url = url_format_cb(term_item["search_term"], i+1, query_limit,
                                    query_sort)


        if not silent_mode:
            print("Downloading HTML " + str(i+1))
            print(request_url)
        
        # Make the request and get the results as a string
        html = requests.get(request_url).content.decode("utf-8")
        
        # If the page has no products, then we have reached the end and there
        # is no point of making new requests (that also means that the user
        # requested all the products that the e-store had under provided
        # search term)
        if is_last_page_cb(html) == True:
            if not silent_mode:
                print("All the products under the search term have been " + \
                        "downloaded!")
                print("No need to download further HTMLs!")
                print("Last downloaded page was an empty page - this will " + \
                        "be skipped during the parsing!")
            return htmls
        
        htmls.append(html)

    return htmls

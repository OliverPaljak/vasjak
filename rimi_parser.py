"""
Parser for the rimi e-store (https://www.rimi.ee/epood/ee)

All constants (such as STORES_DATA and DEFAULT_OPTIONS) can be found in
config.py

Depends on Beautiful Soup (should be installed by the user)
"""

# IMPORTS --------------------------------------------------------------------#
# Native imports
import json
import re
#import time
from urllib.parse import quote

# Library imports
from bs4 import BeautifulSoup

# Project imports
from config import *
import downloader as dwnlder

# PRIVATE FUNCTIONS ----------------------------------------------------------#
def _format_base_url(search_term, page, query_limit, query_sort):
    """
    Format the base url. Should be used as a callback in the download function
    (see downloader.py)

    Parameters
    ----------
    page : int
        The request's page number
    See the download function in downloader.py for information on the other
    parameters

    Returns
    -------
    str 
        The formatted base url
    """
    query_sort = STORES_DATA["rimi"]["query_sort_values"][query_sort]
    base_url = STORES_DATA["rimi"]["base_url"]

    search_term = quote(search_term)
    request_url = base_url.format(page_nr=page, page_size=query_limit,
                                  query=search_term, sort=query_sort)
    return request_url

def _is_last_page(html):
    """
    Check if the given HTML has products in it. Should be used as a callback in
    the download function (see downloader.py)

    Parameters
    ----------
    html : str
        Downloaded/request HTML as a string

    Returns
    -------
    bool
        True if the provided HTML has no products, false otherwise
    """
    return html.find("product-grid__item") == -1

def _get_htmls(term_dict,
               query_limit=DEFAULT_OPTIONS["query_limit"],
               query_sort=DEFAULT_OPTIONS["query_sort"],
               silent_mode=DEFAULT_OPTIONS["silent_mode"]):

    """
    Get the product HTMLs using downloader.

    Parameters
    ----------
    See the download function in downloader.py for information on the 
    parameters

    Returns
    -------
    list
        List of the recieved products pages htmls
    """
     
    return dwnlder.download(term_dict, "rimi", _format_base_url,_is_last_page,
                            query_limit, query_sort, silent_mode)

def _parse(htmls, silent_mode=DEFAULT_OPTIONS["silent_mode"]):
    """
    Parse the recieved htmls (see _get_htmls) to individual products

    Parameters
    ----------
    htmls : list
        The array of HTML strings that were recieved (see _get_htmls and
        downloader.py)
    silent_mode : bool
        If silent mode is not used (silent_mode=False), then the program tries
        to tell user what it is doing. If it is used (silent_mode=True), then
        user notification is kept at bare minimum. Optional, see
        DEFAULT_OPTIONS dictionary in config.py for default value. 
    
    Returns
    -------
    list
        The parsed products
    """

    products = []
    
    if not silent_mode:
        print("\nParsing the downloaded HTMLs...")
    
    i = 1
    # Parse the product pages
    for html in htmls:
        if not silent_mode:
            print("Parsing HTML " + str(i) + "/" + str(len(htmls)))

        # Using beautifulsoup to parse the HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Get all products in the html
        products_html = soup.find_all(class_="product-grid__item")

        if products_html == None:
            continue
        
        # Parse the products
        for product_html in products_html:
            
            # Get product HTML's important elements
            product_div = product_html.find("div")
            product_url = product_html.find("a", class_="card__url")
            product_price_per = product_html.find("p",
                                                  class_="card__price-per")
            
            # If product's div element nor product's url element is not found,
            # then skip current product
            if product_div == None or product_url == None:
                continue
            
            # Get product data as strings
            product_json_str = product_div.get("data-gtm-eec-product")
            product_url = product_url.get("href")
            
            # If product's json string or url is not found, then skip current 
            # product
            if product_json_str == None or product_url == None:
                continue
            
            # If the product_price_per HTML is found, then get the element's
            # text. Ohterwise, product_price_per will be infinity, so that
            # the prodcut would be at the end of the list
            if product_price_per != None:
                product_price_per = product_price_per.string

            if product_price_per == None:
                product_price_per = float("inf")
            
            # If we cannot convert the json string to actual json, then
            # skip current product
            product_json = None
            try:
                product_json = json.loads(product_json_str)
            except:
                continue
            
            if product_price_per != float("inf"):
                # Remove all characters that is not 0-9 or ","
                product_price_per = re.sub(r"[^0-9,]", "", product_price_per)

                # Replace "," with "."
                product_price_per = product_price_per.replace(",", ".")
                
                if product_price_per != "":
                    product_price_per = float(product_price_per)
                else:
                    product_price_per = float("inf")

            # Correct the product URL
            product_url = "https://www.rimi.ee" + product_url

            # Create the product dictionary
            product_dict = {
                "name": product_json["name"],
                "price": product_json["price"],
                "price_per": product_price_per,
                "url": product_url,
                "store": "rimi"
            }
            
            # Add to the products list
            products.append(product_dict)
        i += 1
        
    return products

# PUBLIC FUNCTIONS -----------------------------------------------------------#
def get(term_dict, options=DEFAULT_OPTIONS):
    """
    Get the parsed products from the rimi e-store based on the search term
    dictionary and options.
    
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
    options : dictionary
        The dictionary that contains the user specified options (usually from
        the command line interface - see cli.py). Used to change how the
        program operates. Optional, see DEFAULT_OPTIONS dictionary in config.py
        for default values.

    Returns
    -------
    list
        The parsed (unfiltered) products as dictionaries straight from the
        e-store
    """
    if not options["silent_mode"]:
        print("\n==rimi::" + term_dict["search_term"])
    
    # Download the product pages
    htmls = _get_htmls(term_dict, options["query_limit"],
                       options["query_sort"], options["silent_mode"])

    # Get the products from the product pages
    products = _parse(htmls, options["silent_mode"])
    
    return products

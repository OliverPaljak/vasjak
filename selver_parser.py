"""
Parser for the selver e-store (https://www.selver.ee/)

All constants (such as STORES_DATA and DEFAULT_OPTIONS) can be found in
config.py

Depends on Beautiful Soup (should be installed by the user)
"""

# IMPORTS --------------------------------------------------------------------#
# Native imports
import re
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
    query_sort = STORES_DATA["selver"]["query_sort_values"][query_sort]
    base_url = STORES_DATA["selver"]["base_url"]

    if query_limit < 24:
        query_limit = 24
    elif query_limit < 48:
        query_limit = 48
    else:
        query_limit = 96 
    
    search_term = quote(search_term)
    request_url = base_url.format(_dir=query_sort["_dir"],
                                  page_size=query_limit,
                                  sort=query_sort["sort"],
                                  page_nr=page,
                                  query=search_term)
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
    return html.find("products-grid") == -1

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
    
    return dwnlder.download(term_dict, "selver", _format_base_url,
                            _is_last_page, query_limit, query_sort,
                            silent_mode)

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
        soup = BeautifulSoup(html, "html.parser")
        
        # Get the individual products HTML
        products_html = soup.find(id="products-grid")
        if products_html == None:
            continue

        products_html = products_html.find_all("li")
        if products_html == None:
            continue

        for product_html in products_html:
            
            # Get product HTML's important elements
            product_name = product_html.find("h5", class_="product-name")
            product_price = product_html.find("span", class_="regular-price")
    
            # If important elements are not found, skip this product
            if product_name == None or product_price == None:
                continue
            
            # Get necessary tags
            product_name = product_name.find("a")
            product_price_per = product_price.find("span", class_="unit-price")
            product_price = product_price.find("span", class_="price")
            
            # If the tags are not found, skip this element
            if product_name == None or product_price == None:
                continue
            
            # Get actual data
            product_url = product_name.get("href")
            product_name = product_name.string

            if product_price.string == None:
                product_price = product_price.find("span")
            product_price = product_price.string
            
            if product_url == None or product_name == None or \
                    product_price == None:
                continue

            # If we do not have price per kg/l/etc, then make it equal to 
            # infinity
            if product_price_per != None:
                product_price_per = product_price_per.string
            else:
                product_price_per = float("inf")
            
            # Convert the prices to floats if possible
            # Remove all characters that is not 0-9 or ","
            product_price = re.sub(r"[^0-9,]", "", product_price)
            # Replace "," with "."
            product_price = product_price.replace(",", ".")
            if product_price != "":
                product_price = float(product_price)
            else:
                continue

            if product_price_per != float("inf"):
                product_price_per = re.sub(r"[^0-9,]", "", product_price_per)
                product_price_per = product_price_per.replace(",", ".")
                
                if product_price_per != "":
                    product_price_per = float(product_price_per)
                else:
                    product_price_per = float("inf")

            # Correct the product URL
            product_url = "https:" + product_url

            # Create the product dictionary
            product_dict = {
                "name": product_name,
                "price": product_price,
                "price_per": product_price_per,
                "url": product_url,
                "store": "selver"
            }
            
            # Add to the products list
            products.append(product_dict)
        i += 1
        
    return products

# PUBLIC FUNCTIONS -----------------------------------------------------------#
def get(term_dict, options=DEFAULT_OPTIONS):
    """
    Get the parsed products from the selver e-store based on the search term
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
        print("\n==selver::" + term_dict["search_term"])

    # Download the product pages
    htmls = _get_htmls(term_dict, options["query_limit"],
                       options["query_sort"], options["silent_mode"])
    
    # Get the products from the product pages
    products = _parse(htmls, options["silent_mode"])

    return products

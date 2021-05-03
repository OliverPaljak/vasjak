"""
Module for filtering, sorting, etc. the parsed products.

All constants (such as DEFAULT_OPTIONS) can be found in config.py
"""

# IMPORTS --------------------------------------------------------------------#
# Project imports
from config import *

# PUBLIC FUNCTIONS -----------------------------------------------------------#
def sort(products,
         desc=DEFAULT_OPTIONS["sort_desc"],
         sort_price_per=DEFAULT_OPTIONS["sort_price_per"],
         silent_mode=DEFAULT_OPTIONS["silent_mode"]):
    """
    Sort the parsed products

    Parameters
    ----------
    products : list
        The parsed products dictionaries to be sorted. The structure of the
        dictionaries should be the following:
        {
            "name": <product_name>,
            "price": <price>,
            "price_per": <price_per_kg_liter_etc>,
            "url": <product_url>,
            "store": <store_name>
        }
    desc : bool
        Sort descendingly? Optional, see DEFAULT_OPTIONS dictionary in
        config.py for default value.
    sort_price_per : bool
        Sort by the price_per field? Optional, see DEFAULT_OPTIONS dictionary
        in config.py for default value.
    silent_mode : bool
        If silent mode is not used (silent_mode=False), then the program tries
        to tell user what it is doing. If it is used (silent_mode=True), then
        user notification is kept at bare minimum. Optional, see
        DEFAULT_OPTIONS dictionary in config.py for default value. 

    Returns
    -------
    list
        List of sorted products' dictionaries
    """
    
    if not silent_mode:
        print("Sorting products...")
    products_sorted = products
    if not sort_price_per:
        # Sort by regular price
        products_sorted = sorted(products,
                                 key=lambda product: product["price"],
                                 reverse=desc)
    else:
        # Sort by price per kg/liter/etc
        products_sorted = sorted(products,
                                 key=lambda product: product["price_per"],
                                 reverse=desc)
    if not silent_mode:
        print("Products sorted!")
    return products_sorted


def filter_(term_dict, products,
           search_precise=DEFAULT_OPTIONS["search_precise"],
           search_strict=DEFAULT_OPTIONS["search_strict"],
           silent_mode=DEFAULT_OPTIONS["silent_mode"]):
    """
    Filter out products based on search term and on additional search terms.

    Parameters
    ----------
    term_dict : dictionary
        The dictionary that contains the search term (i.e. the string that the
        query was based on) and additional search term for filtering out the
        products. The stucture of the dictionary should be the following:
        {
            "search_term": <value>,
            "add_terms": [<value_1>, <value_2>]
        }
    products : list
        The products dictionaries to be filtered. The structure of the
        dictionaries should be the following:
        {
            "name": <product_name>,
            "price": <price>,
            "price_per": <price_per_kg_liter_etc>,
            "url": <product_url>,
            "store": <store_name>
        }
    search_precise : bool
        The option to search precisely. It means if the search term is not
        present in the products name, then the product will not be included
        in the filtered products list (that product will be skipped). This 
        option can limit the amount of the products included in the final 
        products list as the normal query search (in the e-store) will return
        every product that has the search term included in the name, 
        description and probably even in the product category - this option
        will force the filterer to look if the search term is present in the
        name. Optional, see DEFAULT_OPTIONS dictionary in config.py for default
        value.
    search_strict : bool
        The option to search strictly. It means that the search term must be
        either a separate word or the end of the word inside the prodcts name.
        For example, if the user searches for "piim" (milk in estonian) and
        strict search is enabled, then it means that products like "piim", 
        "täispiim" (whole milk in estonian) and "kohupiim" (curd in estonian)
        will come out but products like "piimašokolaad" (milk chocolate) and 
        "kohupiimakreem" (curd cream) will be skipped. In technical terms it
        just means that a space will be added to the end of the search term.
        It is important to note that searching strictly has no effect if
        searching precisely is off (search_precise=False). Optional, see
        DEFAULT_OPTIONS dictionary in config.py for default value.
    silent_mode : bool
        If silent mode is not used (silent_mode=False), then the program tries
        to tell user what it is doing. If it is used (silent_mode=True), then
        user notification is kept at bare minimum. Optional, see
        DEFAULT_OPTIONS dictionary in config.py for default value. 
    
    Returns
    -------
    list
        List of filtered products' dictionaries
    """

    filtered_products = []

    search_term = term_dict["search_term"]
    if search_strict:
        search_term += " "

    if not silent_mode:
        print("Filtering products...")
    
    for product in products:
        # Normalize the product name
        norm_product_name = product["name"].lower()
        
        # If we are using precise search and the search term is not found
        # in the (normalized) product name, skip this product
        if search_precise and norm_product_name.find(search_term) == -1:
            continue
        
        # Check if we should include the product to the filtered products list
        # based on additional terms
        include_product = True
        for add_term in term_dict["add_terms"]:
            # Escape backslashes
            escaped_add_term = add_term.replace("\\", "")
            
            # If the search term starts with a "^" then that means that the
            # user wants to check if the additional search term does NOT appear
            # in the product name - if it does appear, then skip that product
            # (i.e. do not include it in the filtered products list).
            #
            # Otherwise, we check if the additional search term appears in the
            # product - if it does not, then we skip it.
            if add_term[0] == "^" and \
                    norm_product_name.find(add_term[1:]) != -1:
                include_product = False
                break
            elif add_term[0] != "^" and \
                    norm_product_name.find(escaped_add_term) == -1:
                include_product = False
                break
        
        if include_product:
            filtered_products.append(product)

    if not silent_mode:
        print("Products filtered!")

    return filtered_products

def limit(products, product_limit=DEFAULT_OPTIONS["product_limit"]):
    """
    Limit the products to the first product_limit products.
    
    Parameters
    ----------
    products : list
        The products dictionaries to be limited
    product_limit : int
        The limit. Optional, see DEFAULT_OPTIONS dictionary in config.py for
        default value.
    
    Returns
    -------
    list
        List of limited products' dictionaries
    """
    if len(products)-1 > product_limit: 
        products = products[:product_limit]
    return products

def get(term_dict, products, options=DEFAULT_OPTIONS):
    """
    Standard function for filtering, sorting and limiting the products based on
    the term dictionary. NOTE: It is also possible to do these actions by
    calling out the individual functions (altough it would be usually wise to
    follow the same order of operation - sort, filter and limit)

    Parameters
    ----------
    term_dict : dictionary
        The dictionary that contains the search term (i.e. the string that the
        query was based on) and additional search term for filtering out the
        products. The stucture of the dictionary should be the following:
        {
            "search_term": <value>,
            "add_terms": [<value_1>, <value_2>]
        }
    products : list
        The products dictionaries to be manipulated. The structure of the
        dictionaries should be the following:
        {
            "name": <product_name>,
            "price": <price>,
            "price_per": <price_per_kg_liter_etc>,
            "url": <product_url>,
            "store": <store_name>
        }
    options : dictionary
        The dictionary that contains the user specified options (usually from
        the command line interface - see cli.py). Used to change how the
        program operates. Optional, see DEFAULT_OPTIONS dictionary in config.py
        for default values.

    Returns
    -------
    list
        List of filtered, sorted and limited products' dictionaries
    """
    if not options["silent_mode"]:
        search_str = term_dict["search_term"]
        for add_term in term_dict["add_terms"]:
            search_str += "+" + add_term
        print("\n==filterer::" + search_str)
    
    # Filter products
    products = filter_(term_dict, products, options["search_precise"],
                       options["search_strict"], options["silent_mode"])
    
    # Sort the filtered products
    products = sort(products, options["sort_desc"], options["sort_price_per"],
                    options["silent_mode"])
    
    # Limit the filtered and sorted products
    products = limit(products, options["product_limit"])
    
    return products

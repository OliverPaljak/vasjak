"""
Module for controlling the command line interface.

All constants (such as DEFAULT_OPTIONS) can be found in config.py
"""

# IMPORTS --------------------------------------------------------------------#
# Native imports
import getopt
import re
import sys
import json
import os

# Project imports
from config import *

# PRIVATE FUNCTIONS ----------------------------------------------------------#
def _get_output_format_str(arg_str):
    """
    Get the string for formatting the output.

    arg_str : str
        The user provided string that the format string is based off. The only
        enabled values/fields in the arg_str are n, p, e, u, s - where:
            n - product name,
            p - price,
            e - price per kg/liter/etc,
            u - product url,
            s - store name
        It is possible to rearrange and leave the fields out (at minimum one
        field is required) and the output will correspond to the provided
        format/arrangment.

        Example: "p n s" - will be translated to fields:
            Price, Product name, Store name

    Returns
    -------
    str
        Corresponding format string if the arg_str was correct, otherwise an
        empty string
    """
    format_str = ""
    formats = re.split(r" ", arg_str)

    for place_holder in formats:
        if place_holder == "n":
            format_str += "{product_name:<50}"
        elif place_holder == "p":
            format_str += "{price:<10}"
        elif place_holder == "e":
            format_str += "{price_per:<20}"
        elif place_holder == "u":
            format_str += "{url:<150}"
        elif place_holder == "s":
            format_str += "{store_name:<10}"
        else:
            return ""
    
    format_str += "\n"
    return format_str

def _get_search_term_dicts(raw_args, input_file=None):
    """
    Get search term dictionaries (that means the string the query is based on +
    additional search terms that are going to be used to filter out products
    during parsing) from the command line and also from the input file.

    Parameters
    ----------
    raw_args : list
        List of command line arguments that the getopt did not recognize
        (i.e. search terms)
    input_file : str
        Path to the input/shopping list file. NOTE: Every search term should be
        on a separate line in the file. Optional.
    
    Returns
    -------
    list
        List of search term dictionaries
    """
    term_dicts = []

    # Try to open the shopping list file if the user has defined it
    if input_file != None:
        try:
            input_file = open(input_file, "r")
        except OSError:
            print("ERROR: Could not open file \"" + str(input_file) + \
                    "\"! Skipping shopping list file reading...")
            input_file = None

    # If we have successfully opened the input file, then read the search terms
    # from it
    if input_file != None:
        for line in input_file:
            raw_args.append(line.strip())
        input_file.close()
    
    # Create a term dictionary for every search string
    for search_str in raw_args:
        # Skeleton for the term dictionary
        current_dict = {
            "search_term": "",
            "add_terms": []
        }

        if search_str.find(":") != -1:
            terms = re.split(r"(?<!\\):", search_str)

            # Remove empty string from the terms array
            terms[:] = [term for term in terms if term != '']
            
            # First term is always the term that the download request is based
            # on
            current_dict["search_term"] = terms[0].lower()
            
            # Get additional terms
            terms = terms[1:]
            for term in terms:
                escaped_term = term.replace("\\", "").lower()
                if term.find("^") == 1 and term.find("\\") == 0:
                    escaped_term = "\\^" + escaped_term[1:]
                
                current_dict["add_terms"].append(escaped_term)
            
            # Remove duplicates
            current_dict["add_terms"] = list(dict.fromkeys(
                                             current_dict["add_terms"]))
        else:
            current_dict["search_term"] = search_str

        term_dicts.append(current_dict)

    if len(term_dicts) == 0:
        print("ERROR: No search terms were found! Aborting...\n")
        print_help()
        sys.exit()

    return term_dicts

# PUBLIC FUNCTIONS -----------------------------------------------------------#
def exit_():
    """
    Exit from the program
    """
    # Uncomment lines 152 ja 153 if you want to prevent the python terminal
    # from closing on windows
    #if os.name == 'nt':
        #input("Press enter to continue...")
    sys.exit()

def print_result(result_dict, options=DEFAULT_OPTIONS):
    """
    Print the results

    Parameters
    ----------
    result_dict : dictionary
        The dictionary that contains the results. Structure should be the
        following:
        {
            "<search_term>": [product_dict1, product_dict2, ...],
            "<another_search_term>": [product_dict1, product_dict2, ...]
        }
    options : dictionary
        The dictionary that contains the user specified options (usually from
        the command line interface). Used to change how the program operates.
        Optional, see DEFAULT_OPTIONS dictionary in config.py for default
        values.
    """
    result = ""
    
    if options["human_read"] == False:
        result = json.dumps(result_dict, indent=4)
        print(result)
        return
    
    for search_str in result_dict:
        result += "\n# Keyword: " + search_str + "\n"
        result += options["out_str"].format(product_name="Name", price="Price",
                                            price_per="Price per kg/l/etc",
                                            url="URL", store_name="Store")
        for product in result_dict[search_str]:
            if product["price_per"] == float("inf"):
                product["price_per"] = "N/A"

            if len(product["name"]) > 50:
                product["name"] = product["name"][:47] + "..."
            
            result += options["out_str"].format(product_name=product["name"],
                                                price=product["price"],
                                                price_per=product["price_per"],
                                                url=product["url"],
                                                store_name=product["store"]\
                                                        .lower().capitalize())
    print(result)

def print_help():
    """
    Print help text for the command line interface.

    For reference the help text is the following:
    Usage:
        pythone3 main.py [OPTION...] SEARCH_TERM[:ADDITIONAL_TERM...]...

    """

    help_text = """Usage:
    python3 main.py [OPTION...] SEARCH_TERM[:ADDITIONAL_TERM...]...
Options:
    -c SECONDS
        Change the cache keep-alive time period. 0 disables the cache (no
        reading/writing will be done from/to the cache file). Default is
        {default_opts[cache_time]} second(s).

    -d  Sort descendingly (used in the filtering process). See also the -k
        option. By default {sort_desc}.
    
    -f FILE
        Shopping list/input file for search terms. Every search term (with
        its additional terms) should be on its separate line. Can be used
        together with search terms defined on the command line.

    -g  Glue duplicate main terms together. For more information see the
        Additional terms section at end of this help text.

    -h  Print help

    -j  Format the output as JSON, otherwise the output is in human readable
        plain text. By default {human_read}.

    -k default|asc|desc|asc_per|desc_per
        Query sort. When making requests to the e-stores use one of these
        sorting options in the request query. This is different from using the
        options -d and -p as this option will request the products in a
        particular order from e-stores rather than sort them in the filtering
        process/during program execution (i.e. sort using e-store own sorting
        or sort using the request). It is still possible to use program sorting
        (options -d and -p) together with this option. Altough it might seem
        like a good idea to let the e-store handle the sorting, then in reality
        using this option will probably result in inaccurate results when the
        requested product count is small (< 500) and also all the listed
        options do not work in all e-stores. For starters, it is recommended to
        use the default value but experimentation is key...

        default - do not sort at all/use the e-store's default way of
                  sorting (this usually means by relevance or by
                  popularity). Gives the most accurate results.
        asc - sort ascendigly
        desc - sort descendingly
        asc_per - sort ascendingly but use the price per kg/liter/etc
        desc_per - sort descendingly but use the price per kg/liter/etc

        Rimi supports all the values, selver supports default, asc and desc
        values. By default the {default_opts[query_sort]} value is used.

    -l NUMBER
        Limit the number of products in the answers (per search term). By
        default {default_opts[product_limit]}.

    -m none|precise|strict
        Search mode. This option controls how is the search conducted during
        the filtreation process.

        If value "none" is used, then this means that we relay purely on the
        e-store results (no filtering is taken place, except for the additional
        terms if they are provided).

        If value "precise" is used, then it means that the main search term
        (the search term that the query is based off) be inside the product's
        name - often times the e-stores return products that do not have the
        requested search term inside the product names but appear for example
        in the product's description, category etc. Precise search mode
        prevents this.

        Strict search mode means that the search term must be either a separate
        word or the end of the word inside the products name. For example, if
        the user searches for "piim" (milk in estonian) and strict search is
        enabled, then it means that products like "piim", "täispiim" (whole
        milk in estonian) and "kohupiim" (curd in estonian) will come out but
        products like "piimašokolaad" (milk chocolate) and "kohupiimakreem"
        (curd cream) will be skipped. In technical terms it just means that a
        space will be added to the end of the search term.

        Further narrowing down can be achieved using additional search terms.
        By default "{srch_mode}".

    -o FORMAT
        The user provided string that the format string is based off. The only
        enabled values/fields in the arg_str are n, p, e, u, s - where:
            n - product name,
            p - price,
            e - price per kg/liter/etc,
            u - product url,
            s - store name
        It is possible to rearrange and leave the fields out (at minimum one
        field is required) and the output will correspond to the provided
        format/arrangment.

        Example: "p n s" - will be translated to fields:
            Price, Product name, Store name

        NOTE: Does not affect the non-human readable (JSON) output

    -p  Sort by price per kg/liter/etc. By default {s_per}.

    -q NUMBER
        Query limit. Limit the number of requested/downloaded products. By
        default {default_opts[query_limit]}

    -s  Silent mode. Do not print anything except the end result. By default
        {slt_mode}.

    Default options can be changed in the config.py file.

Additional terms:
    Additional terms can be used to further narrow down search results. The
    basic usage for additional search terms is the following:
        main_term:add_term1:add_term2:^neg_add_term

    For example "piim:1l:2,5%:^alma" syntax translation is the following:
        piim (milk in estonian) - is the main search term
        1l - is the first additional search term
        2,5% - is the second additional search term
        ^alma - is the third additioanl search term
    and means the following (with precise searching mode): include products
    that have the strings "piim", 1l and 2,5% inside their product name but
    does not have the string "alma" in them (NOTE: if precise or strict
    searching mode is not used, then the word "piim", the main search term, 
    does not have to be inside the product's name)

    As one can see, it is like a logical query where every additional search
    term must be inside (or not be inside) the product's name (show the product
    if the name has <term1> AND <term2> AND <term3> AND NOT <term4> ...).
    To use inversion, just put "^" before an additional search term.

    It is also possible to make OR statments. For this comes handy the -g
    option (glue duplicate main terms). The -g option says that do not filter
    duplicate main terms separately.

    For example not using -g option on a query like this one: 
        python3 main.py piim:alma piim:farmi
    would just return two (separate) result/lists (first list: milks that have
    the string "alma" in their names and second list: milks that have the
    the string "farmi" in their names). But using the -g option:
        python3 main.py -g piim:alma piim:farmi
    affects the program so that it would return only one list based on the
    terms - it translates to: show me products that have the words "piim" and
    "alma" in their titles OR show me products that have the words "piim" and
    "farmi" in their titles (in a single list).

    With these tools it is possible to do some advanced queries:
        python3 main.py -g piim:alma piim:farmi piim:rimi:^basic
    which translates to (when using presice or strict searching mode):
    show me products that have the words
        (piim AND alma) OR (piim AND farmi) OR (piim AND rimi AND NOT basic)
    in their names.

    NOTE: The -g option puts only the duplicate terms in a single list. For
    example:
        python3 main.py -g piim:alma piim:farmi vorst:rakvere vorst:rimi
    would put milks ("piim") on the same list and sausageses ("vorst") on
    a different list.

    NOTE: If you want to check whether the characaters ":" and "^" are in the
    product's name, then escape these characters with a backslash (e.g. \\: and
    \\^)

Examples:
    python3 main.py piim
        Search for piim (milk in estonian) using the default values as defined
        in the config.py
    
    python3 main.py piim juust
        Search for piim (milk in estonian) and juust (cheese in estonian) using
        the default values as defined in the config.py
    
    python3 main.py -q 20 vorst
        Search for vorst (sausage in estonian) but limit the requested products
        to 20 (per store)
    
    python3 main.py -q 20 -l 10 -p juust:viil:^sulatatud
        Search for juust (cheese in estonian) but include only results where
        the word "viil" (slice in estonian) appears but the word "sulatatud"
        does not appear. Also limit the requested products to 20 (per store)
        but show only the first 10 of the parsed products.
    
    python3 main.py -g piim:alma piim:farmi
        Search for piim (milk in estonian) but show only results that have
        the word "alma" or "farmi" in them (milk producers in Estonia)
    """
    
    opts = DEFAULT_OPTIONS
    search_mode = "none"

    if opts["search_precise"] and opts["search_strict"]:
        search_mode = "strict"
    elif opts["search_precise"]:
        search_mode = "precise"
    
    help_text = help_text.format(default_opts=opts,
         sort_desc="not used" if not opts["sort_desc"] else "used",
         human_read="used" if not opts["human_read"] else "not used",
         srch_mode=search_mode,
         s_per="not used" if not opts["sort_price_per"] else "used",
         slt_mode="not used" if not opts["silent_mode"] else "used")

    print(help_text)

def get_opts(argv):
    """
    Get options and arguments from the command line.

    Parameters
    ----------
    argv : list
        List of command line options and arguments (without the program's
        name). For more info on the options see the print_help function in this
        module.
    
    Returns
    -------
    dictionary
        Dictionary with all the user defined options' values in it
    """
    
    opts_dict = DEFAULT_OPTIONS.copy()
    input_file = None
    
    try:
        opts, raw_args = getopt.getopt(argv, "c:df:ghjk:l:m:o:pq:s")
    except getopt.GetoptError as err:
        print("ERROR: " + str(err).capitalize() + "\n")
        print_help()
        exit_()

    for opt, arg in opts:
        if opt == "-h":
            print_help()
            exit_()
        
        # For more info on the options see the print_help function in this
        # module

        # Cache time
        if opt == "-c":
            opts_dict["cache_time"] = int(arg)
        # Sort descendingly
        elif opt == "-d":
            opts_dict["sort_desc"] = True
        # Input file/shopping list file
        elif opt == "-f":
            input_file = arg
        # Glue duplicates
        elif opt == "-g":
            opts_dict["glue_duplicates"] = True
        # Non-human readable output (output as JSON)
        elif opt == "-j":
            opts_dict["human_read"] = False
        # Query sort value
        elif opt == "-k":
            if arg == "default":
                opts_dict["query_sort"] = "default"
            elif arg == "asc":
                opts_dict["query_sort"] = "asc"
            elif arg == "desc":
                opts_dict["query_sort"] = "desc"
            elif arg == "asc_per":
                opts_dict["query_sort"] = "asc_per"
            elif arg == "desc_per":
                opts_dict["query_sort"] = "desc_per"
            else:
                print_help()
                exit_()
        # Product limit
        elif opt == "-l":
            opts_dict["product_limit"] = abs(int(arg))
        # Search mode
        elif opt == "-m":
            if arg == "none":
                opts_dict["search_precise"] = False
                opts_dict["search_strict"] = False
            elif arg == "precise":
                opts_dict["search_precise"] = True
                opts_dict["search_strict"] = False
            elif arg == "strict":
                opts_dict["search_precise"] = True
                opts_dict["search_strict"] = True
            else:
                print_help()
                exit_()
        # Format/rearrange output
        elif opt == "-o":
            out_str = _get_output_format_str(arg)
            
            if out_str != "":
                opts_dict["out_str"] = out_str
            else:
                print("ERROR: Invalid format string! Aborting...\n")
                print_help()
                exit_()
        # Sort by price per kg/liter/etc
        elif opt == "-p":
            opts_dict["sort_price_per"] = True
        # Query limit
        elif opt == "-q":
            opts_dict["query_limit"] = int(arg)
        # Silent mode
        elif opt == "-s":
            opts_dict["silent_mode"] = True

    opts_dict["search_term_dicts"] = _get_search_term_dicts(raw_args, input_file)

    return opts_dict

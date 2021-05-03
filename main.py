"""
Main module/entry point for vasjak

Get products from different stores and sort them by price

Authors: Sten-Markus Vaska (project lead) and Oliver Paljak (developer)

License: AGPLv3+
"""

# IMPORTS --------------------------------------------------------------------#
# Native imports
import sys
import getopt

# Project imports
import filterer as filterer
import cli as cli
import cacher as cacher

# MAIN -----------------------------------------------------------------------#
def main(argv):
    """
    Main/start function for <project_name>

    Parameters
    ----------
    argv : list
        Command line arguments without the program's name
    """
    opts = cli.get_opts(argv)

    cacher.read_from_file(opts["cache_file"], opts["cache_time"],
                          opts["silent_mode"])

    term_dicts = opts["search_term_dicts"]

    # If the "glue" option is used, find the duplicate search terms
    duplicate_terms = []
    if opts["glue_duplicates"]:
        all_search_terms = []
        duplicate_counter = {}
        
        for term_dict in term_dicts:
            all_search_terms.append(term_dict["search_term"])
    
        for search_term in all_search_terms:
            if search_term not in duplicate_counter:
                duplicate_counter[search_term] = 1
            else:
                duplicate_counter[search_term] += 1

        for search_term in duplicate_counter:
            if duplicate_counter[search_term] > 1 and\
                    search_term not in duplicate_terms:

                duplicate_terms.append(search_term)
         
    result_dict = {}
    
    # Get results for the glued terms
    if len(duplicate_terms) > 0:
        result_keys = {}
        filtered_products_dict = {}
        
        for term_dict in term_dicts:
            search_term = term_dict["search_term"]
            if search_term not in duplicate_terms:
                continue

            if search_term not in filtered_products_dict:
                filtered_products_dict[search_term] = []
            
            if search_term not in result_keys:
                result_keys[search_term] = search_term + "::"
            else:
                result_keys[search_term] += "|"
            
            result_keys[search_term] += "("
            for add_term in term_dict["add_terms"]:
                result_keys[search_term] += "&" + add_term
            result_keys[search_term] += ")"
            
            rimi_products = cacher.get(term_dict, "rimi", opts)
            selver_products = cacher.get(term_dict, "selver", opts)

            filtered_products_dict[search_term] += filterer.filter_(term_dict, 
                    rimi_products + selver_products, opts["search_precise"],
                    opts["search_strict"], opts["silent_mode"])

        for search_term in filtered_products_dict:
            result_key = result_keys[search_term]
            filtered_products = filtered_products_dict[search_term]
            result = filterer.sort(filtered_products, opts["sort_desc"],
                                   opts["sort_price_per"], opts["silent_mode"])
            
            result = filterer.limit(result, opts["product_limit"])
            result_dict[result_key] = result

    # Get results from normal (not-glued) terms
    for term_dict in term_dicts:
        if term_dict["search_term"] in duplicate_terms:
            continue
        
        rimi_products = cacher.get(term_dict, "rimi", opts)
        selver_products = cacher.get(term_dict, "selver", opts)

        result = filterer.get(term_dict, rimi_products + selver_products, opts)

        result_key = term_dict["search_term"]
        if len(term_dict["add_terms"]) > 0:
            result_key += "::"

        for add_term in term_dict["add_terms"]:
            result_key += "&" + add_term
        result_dict[result_key] = result
    
    # Write current cache to the cache file
    cacher.write_to_file(opts["cache_file"], opts["cache_time"],
                         opts["silent_mode"])
    
    # Print the results to standard output
    cli.print_result(result_dict, opts)
    
    cli.exit_()


# ENTRY POINT ----------------------------------------------------------------#
if __name__ == "__main__":
    main(sys.argv[1:])

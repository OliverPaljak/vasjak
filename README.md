# vasjak

## About
vasjak is an estonian e-store price comparator. It aims to make online
grocery shopping easier and cheaper.

## How to install

### Install libraries

The program depends BeautifulSoup and Requests libraries. Probably the most
sanest way is to install them with pip (use root privileges if necessary):

`pip install beautifulsoup4`

`pip install requests`

For more information please refer to
[BeautifulSoup](https://pypi.org/project/beautifulsoup4/) and
[requests](https://pypi.org/project/requests/).

### Install the program

Just clone the repo and run the main.py with python3.

For example: `python3 main.py piim`

## Usage

Run `python3 main.py -h` or if you like to read text from github:

```
Usage:
    python3 main.py [OPTION...] SEARCH_TERM[:ADDITIONAL_TERM...]...

Options:
    -c SECONDS
        Change the cache keep-alive time period. 0 disables the cache (no
        reading/writing will be done from/to the cache file). Default is
        43200 second(s).

    -d  Sort descendingly (used in the filtering process). See also the -k
        option. By default not used.
    
    -f FILE
        Shopping list/input file for search terms. Every search term (with
        its additional terms) should be on its separate line. Can be used
        together with search terms defined on the command line.

    -g  Glue duplicate main terms together. For more information see the
        Additional terms section at end of this help text.

    -h  Print help

    -j  Format the output as JSON, otherwise the output is in human readable
        plain text. By default not used.

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
        values. By default the default value is used.

    -l NUMBER
        Limit the number of products in the answers (per search term). By
        default 20.

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
        By default "precise".

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

    -p  Sort by price per kg/liter/etc. By default not used.

    -q NUMBER
        Query limit. Limit the number of requested/downloaded products. By
        default 100

    -s  Silent mode. Do not print anything except the end result. By default
        not used.

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
    product's name, then escape these characters with a backslash (e.g. \: and
    \^)

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
```

## Authors

Sten-Markus Vaska (project lead) and Oliver Paljak (developer).


def determine_job_experience_options(exp: str, options: dict = None) -> list:
    """
    Returns list of options for experience range
    :param exp:
    :param options:
    :return:
    """
    # in case user inputs either one year or range (e.g. `0` or `1-2`)
    start_exp, *end_exp = exp.split("-")
    print(start_exp, end_exp)

    options = {
        0: "without experience",
        1: "up to 1 year",
        2: "1-2 years",
        3: "2-5 years",
        4: "2-5 years",
        5: "2-5 years",
        6: "more than 5 years",
        7: "more than 5 years",
        8: "more than 5 years",
        9: "more than 5 years",
        10: "more than 5 years",
    }
    # TODO: change options according to the each website, i mean for each scraper class make it's own options

    if end_exp:
        end_exp = int(end_exp[0])
        exp_range = list(range(int(start_exp), end_exp + 1))
        return list(set([options.get(year) for year in exp_range]))
    else:
        return [options.get(int(start_exp)), ]

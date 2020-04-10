def format_drinks_short(drinks):
    result_list = []
    for drink in drinks:
        result_list.append(drink.short())
    return result_list


def format_drinks_long(drinks):
    result_list = []
    for drink in drinks:
        result_list.append(drink.long())
    return result_list

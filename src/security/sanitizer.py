import nh3

def sanitize_json(data, **nh3_options):
    """
    Recursively sanitize all strings in a JSON-like Python object
    using nh3.clean().
    """
    if isinstance(data, str):
        return nh3.clean(data, **nh3_options)
    elif isinstance(data, dict):
        return {k: sanitize_json(v, **nh3_options) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_json(item, **nh3_options) for item in data]
    else:
        return data  # numbers, booleans, None stay unchanged


def remove_dollar_from_keys(data):
    """
    Recursively remove '$' characters from all keys in a JSON-like dict/list.
    """
    if isinstance(data, dict):
        new_dict = {}
        for k, v in data.items():
            clean_key = k.replace("$", "")
            new_dict[clean_key] = remove_dollar_from_keys(v)
        return new_dict
    elif isinstance(data, list):
        return [remove_dollar_from_keys(item) for item in data]
    else:
        return data  # Base case: primitive types remain unchanged
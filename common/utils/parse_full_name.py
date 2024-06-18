import re
from django.template.defaultfilters import truncatechars

regex = "^M(?:d|r|s)(?:\.|\s)|^Mrs(?:\.|\s)|^Miss(?:\.|\s)|^PhD(?:\.|\s)|^Dr(?:\.|\s)|^Eng(?:\.|\s)"


def parse_full_name(full_name: str) -> tuple:
    """
    Parse a string containing a fully qualified name and 
    process the following name prefixes:
    Dr., Eng., Md., Miss, Mr., Mrs., Ms., PhD.
    
    Args:
        full_name (str): full name

    Returns:
        tuple: first name, middle name, last name
    """
    first_name = middle_name = last_name = ''
    
    if full_name:
        full_name = ''.join(full_name.splitlines())
        full_name = re.sub(' +', ' ', full_name)
        prefix = re.findall(regex, full_name, re.IGNORECASE)
        if prefix:
            prefix = prefix[0].rstrip()
            full_name = re.sub(prefix, '', full_name)
            prefix = prefix[0:1].upper() + prefix[1:]
        splitted_name = full_name.split(" ")
        splitted_name = list(filter(None, splitted_name))
        if len(splitted_name) == 1:
            first_name = full_name
        elif len(splitted_name) == 2:
            first_name = splitted_name[0]
            last_name = splitted_name[1]
        else:
            first_name = splitted_name[0]
            middle_name = truncatechars(" ".join(splitted_name[1:-1]), 90)
            last_name = splitted_name[-1]
        if prefix:
            first_name = f"{prefix} {first_name}"
    return first_name, middle_name, last_name


def parse_contacts_name(obj) -> None:
    full_name = ' '.join(filter(None, (obj.first_name, obj.middle_name, obj.last_name)))
    obj.first_name, obj.middle_name, obj.last_name = parse_full_name(full_name)

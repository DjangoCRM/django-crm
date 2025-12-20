import re
from django.conf import settings
from django.template.defaultfilters import truncatechars


"""
Build a regex that matches any prefix from settings.NAME_PREFIXES:
- case-insensitive
- optional dot allowed, with optional spaces before the dot (e.g. 'Dr .')
- matches whole token and prefers longer prefixes first
"""
# normalize and deduplicate (remove trailing dots)
tokens = {p.strip().rstrip('.') for p in settings.NAME_PREFIXES if p}
# prefer longer tokens first to avoid partial matches (e.g. 'Mister' vs 'Mr')
ordered = sorted(tokens, key=len, reverse=True)
escaped = [re.escape(t) for t in ordered]
# match at token boundary, allow optional spaces before an optional dot, ensure followed by whitespace or end
pattern = r'(?:' + '|'.join(escaped) + r')(?:\.|\s)'
PREFIX_REGEX = re.compile(pattern, re.IGNORECASE)


def parse_full_name(full_name: str) -> tuple:
    """
    Parse a string containing a fully qualified name and 
    process the settings.NAME_PREFIXES (the first name may contain a prefix).

    Args:
        full_name (str): full name

    Returns:
        tuple: first name, middle name, last name
    """
    first_name = middle_name = last_name = prefix = ''
    
    if full_name:
        full_name = ''.join(full_name.splitlines())
        full_name = re.sub(' +', ' ', full_name)
        m = re.search(PREFIX_REGEX, full_name)
        if m:
            prefix = m.group(0).rstrip()
            full_name = re.sub(prefix, '', full_name)
            prefix = prefix[0:1].upper() + prefix[1:] # "PhD".title() -> "Phd"
        split_name = full_name.split(" ")
        split_name = list(filter(None, split_name))
        if len(split_name) == 1:
            first_name = full_name
        elif len(split_name) == 2:
            first_name = split_name[0]
            last_name = split_name[1]
        else:
            first_name = split_name[0]
            middle_name = truncatechars(" ".join(split_name[1:-1]), 90)
            last_name = split_name[-1]
        if prefix:
            first_name = f"{prefix} {first_name}"
    return first_name, middle_name, last_name


def parse_contacts_name(obj) -> None:
    full_name = ' '.join(filter(None, (obj.first_name, obj.middle_name, obj.last_name)))
    obj.first_name, obj.middle_name, obj.last_name = parse_full_name(full_name)

import re
import secrets

ticket_str = '  - [ticket:{}] '

        
def new_ticket():
    return secrets.token_urlsafe(8)


def get_ticket_str(ticket): 
    return ticket_str.format(ticket)


def get_ticket(lst):
    txt = ''.join(lst)
    result = re.search(r"\[ticket:(.+?)]", txt)
    return result.group(1) if result else None

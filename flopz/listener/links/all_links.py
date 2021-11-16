from flopz.listener.links.socketcan_link import SocketcanLink

_all_links = [
    SocketcanLink,
]

def get_all_links():
    return _all_links

def get_link_by_name(name: str):
    for l in _all_links:
        if l.name() == name:
            return l
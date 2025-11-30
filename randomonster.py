from requests import request


# request is completed at time of import when app server starts
_base_url = 'https://www.dnd5eapi.co/api/2014/'
_endpoints = ('magic-items', 'monsters', 'spells')
_headers = {'Accept': 'application/json'}

# track used names so random names can be recycled as presets are deleted
used_names = set()
names = set()
# append item names to the "names" set for each of the 5e API endpoints
for _url in map(_base_url.__add__, _endpoints):
    _response = request('GET', _url, headers=_headers)
    names = names.union(
        {item['name'] for item in _response.json().get('results', [])}
    )


def get_dnd() -> str | None:
    """Return a random dnd item, monster, or spell name"""
    try:
       choice = names.pop()
       used_names.add(choice)
       return choice
    except KeyError, IndexError:  # set empty
        return None

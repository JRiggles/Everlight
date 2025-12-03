from asyncio import gather, run
from httpx import AsyncClient


_base_url = 'https://www.dnd5eapi.co/api/2014/'
_headers = {'Accept': 'application/json'}
_endpoints = ('magic-items', 'monsters', 'spells')


async def _fetch_names() -> set[str]:
    """Fetch item names from the 5e API endpoints asynchronously."""
    _names = set()
    async with AsyncClient(base_url=_base_url, headers=_headers) as client:
        request_tasks = [client.get(endpoint) for endpoint in _endpoints]
        for response in await gather(*request_tasks):
            if response.status_code == 200:
                _names = _names.union(
                    {i['name'] for i in response.json().get('results', [])}
                )
    return _names


def get_dnd() -> str | None:
    """Return a random dnd item, monster, or spell name."""
    try:
        choice = names.pop()
        used_names.add(choice)
        return choice
    except KeyError:  # set empty
        return None


# run fetch_names coroutine to populate set of names
names = run(_fetch_names())
# track used names so random names can be recycled as presets are deleted
used_names = set()


if __name__ == '__main__':
    print(names)

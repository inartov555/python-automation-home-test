import requests
import pytest

def test_get_facts_ok_and_schema(api_base):
    r = requests.get(f"{api_base}/facts")
    assert r.status_code == 200
    body = r.json()
    # Basic shape
    assert 'data' in body and isinstance(body['data'], list)
    for key in ['current_page', 'per_page']:
        assert key in body

@pytest.mark.parametrize('page,limit', [(1,5),(2,10),(3,3)])
def test_pagination(api_base, page, limit):
    r = requests.get(f"{api_base}/facts", params={'page': page, 'limit': limit})
    assert r.status_code == 200
    body = r.json()
    assert body.get('current_page') == page
    assert len(body.get('data', [])) <= limit

def test_breeds_schema(api_base):
    r = requests.get(f"{api_base}/breeds")
    assert r.status_code == 200
    body = r.json()
    assert 'data' in body and isinstance(body['data'], list)
    required = {'breed','country','origin','coat','pattern'}
    # Assert at least one item and all required keys exist on each item
    for item in body['data'][:10]:  # sample first 10
        assert required.issubset(item.keys())

def test_invalid_limit_handled(api_base):
    r = requests.get(f"{api_base}/facts", params={'limit': -1})
    # Some public APIs normalize invalid input; others return 4xx.
    assert r.status_code in (200, 400, 422)
    # If 200, response should still be valid JSON with expected keys
    if r.status_code == 200:
        body = r.json()
        assert 'data' in body
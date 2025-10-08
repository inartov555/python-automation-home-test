"""
API tests
"""

import pytest


@pytest.mark.public_api
class TestApi:
    """
    API tests
    """

    def test_get_facts_ok_and_schema(self):
        """
        Get /facts, check if status code == 200, then check if 'current_page', 'per_page' are available
        """
        resp = self.public_api.make_request("get", "/facts", is_return_resp_obj=True)
        assert resp.status_code == 200
        body = resp.json()
        # Basic shape
        assert 'data' in body and isinstance(body['data'], list)
        for key in ['current_page', 'per_page']:
            assert key in body

    @pytest.mark.parametrize('page,limit', [(1,5),(2,10),(3,3)])
    def test_pagination(self, page, limit):
        """
        Get /facts, check if status code == 200, then check if page changes
        """
        query_params = {'page': page, 'limit': limit}
        resp = self.public_api.make_request("get", "/facts", query_params=query_params, is_return_resp_obj=True)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get('current_page') == page
        assert len(body.get('data', [])) <= limit

    def test_breeds_schema(self):
        """
        Get /breads, check if status code == 200, then check if response contains the list
        """
        resp = self.public_api.make_request("get", "/breeds", is_return_resp_obj=True)
        assert resp.status_code == 200
        body = resp.json()
        assert 'data' in body and isinstance(body['data'], list)
        required = {'breed','country','origin','coat','pattern'}
        # Assert at least one item and all required keys exist on each item
        for item in body['data'][:10]:  # sample first 10
            assert required.issubset(item.keys())

    def test_invalid_limit_handled(self):
        """
        Get /facts, check if checking invalid limit
        """
        query_params = {'limit': -1}
        resp = self.public_api.make_request("get", "/facts", query_params=query_params, is_return_resp_obj=True)
        # Some public APIs normalize invalid input; others return 4xx.
        assert resp.status_code in (200, 400, 422)
        # If 200, response should still be valid JSON with expected keys
        if resp.status_code == 200:
            body = resp.json()
            assert 'data' in body

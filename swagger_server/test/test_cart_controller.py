# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.cart_body import CartBody  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.product import Product  # noqa: E501
from swagger_server.test import BaseTestCase


class TestCartController(BaseTestCase):
    """CartController integration test stubs"""

    def test_add_to_cart(self):
        """Test case for add_to_cart

        
        """
        body = CartBody()
        response = self.client.open(
            '/cart',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_cart_products(self):
        """Test case for get_cart_products

        
        """
        query_string = [('user_id', 56)]
        response = self.client.open(
            '/cart',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_remove_from_cart(self):
        """Test case for remove_from_cart

        
        """
        query_string = [('type', 'song')]
        response = self.client.open(
            '/cart/{productId}'.format(product_id=56),
            method='DELETE',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()

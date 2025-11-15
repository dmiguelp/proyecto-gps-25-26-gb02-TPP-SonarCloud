# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.purchase import Purchase  # noqa: E501
from swagger_server.test import BaseTestCase


class TestPurchasesController(BaseTestCase):
    """PurchasesController integration test stubs"""

    def test_set_purchase(self):
        """Test case for set_purchase

        Set a product as purchased by the user.
        """
        body = Purchase()
        response = self.client.open(
            '/purchase',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()

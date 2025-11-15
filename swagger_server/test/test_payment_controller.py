# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.payment_method import PaymentMethod  # noqa: E501
from swagger_server.test import BaseTestCase


class TestPaymentController(BaseTestCase):
    """PaymentController integration test stubs"""

    def test_add_payment_method(self):
        """Test case for add_payment_method

        Add a new payment method
        """
        body = PaymentMethod()
        response = self.client.open(
            '/payment',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_payment_method(self):
        """Test case for delete_payment_method

        Delete a payment method by ID.
        """
        response = self.client.open(
            '/payment/{paymentMethodId}'.format(payment_method_id='payment_method_id_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()

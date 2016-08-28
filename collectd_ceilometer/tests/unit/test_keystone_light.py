# -*- coding: utf-8 -*-

# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2015 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Plugin tests"""

from __future__ import unicode_literals

from collectd_ceilometer import keystone_light
from collectd_ceilometer.keystone_light import ClientV2
from collectd_ceilometer.keystone_light import MissingServices
import mock
import unittest


class KeystoneLightTest(unittest.TestCase):
    """Test the keystone light client"""

    def setUp(self):
        super(KeystoneLightTest, self).setUp()

        self.test_authtoken = "c5bbb1c9a27e470fb482de2a718e08c2"
        self.test_public_endpoint = "http://public_endpoint"
        self.test_internal_endpoint = "http://iternal_endpoint"
        self.test_region = "RegionOne"

        response = {'access': {
            "token": {
                "issued_at": "2015-09-04T08:59:09.991646",
                "expires": "2015-09-04T09:59:09Z",
                "id": self.test_authtoken,
                "tenant": {
                    "enabled": True,
                    "description": None,
                    "name": "service",
                    "id": "fdeec62f6c794c8dbfda448a83de9ce2"
                },
                "audit_ids": [
                    "Pig7hVfGQjSuUnt1Hc5mCg"
                ]
            },
            "serviceCatalog": [{
                "endpoints_links": [],
                "endpoints": [{
                    "adminURL": "http://10.237.214.74:8777/",
                    "region": self.test_region,
                    "publicURL": self.test_public_endpoint + '/',
                    "internalURL": self.test_internal_endpoint,
                    "id": "ac95b1a24a854ec7a4b63b08ed4cbd83"
                }],
                "type": "metering",
                "name": "ceilometer"
            }, ],
        }}

        self.mock_response = mock.Mock()
        self.mock_response.json.return_value = response

    @mock.patch('collectd_ceilometer.keystone_light.requests.post')
    def test_refresh(self, mock_post):
        """Test refresh"""

        mock_post.return_value = self.mock_response

        client = ClientV2("test_auth_url", "test_username",
                          "test_password", "test_tenant")
        client.refresh()

        self.assertEqual(mock_post.call_count, 1)
        self.assertEqual(client.auth_token, self.test_authtoken)

        expected_args = {
            'headers': {'Accept': 'application/json'},
            'json': {
                'auth': {
                    'tenantName': u'test_tenant',
                    'passwordCredentials': {
                        'username': u'test_username',
                        'password': u'test_password'
                    }
                }
            }
        }

        self.assertEqual(mock_post.call_args[0], (u'test_auth_url/tokens',))
        self.assertEqual(mock_post.call_args[1], expected_args)

    @mock.patch('collectd_ceilometer.keystone_light.requests.post')
    def test_getservice_endpoint(self, mock_post):
        """Test getservice endpoint"""

        mock_post.return_value = self.mock_response

        client = ClientV2("test_auth_url", "test_username",
                          "test_password", "test_tenant")
        client.refresh()

        endpoint = client.get_service_endpoint('ceilometer')
        self.assertEqual(endpoint, self.test_internal_endpoint)

        endpoint = client.get_service_endpoint('ceilometer', 'publicURL')
        self.assertEqual(endpoint, self.test_public_endpoint)

        endpoint = client.get_service_endpoint('ceilometer', 'publicURL',
                                               self.test_region)
        self.assertEqual(endpoint, self.test_public_endpoint)

        with self.assertRaises(MissingServices):
            client.get_service_endpoint('badname')

    @mock.patch('collectd_ceilometer.keystone_light.requests.post')
    def test_getservice_endpoint_error(self, mock_post):
        """Test getservice endpoint error"""

        response = {'access': {
            "token": {
                "id": "authtoken",
            },
            "serviceCatalog": [{
                "endpoints_links": [],
                "endpoints": [],
                "type": "metering",
                "missingname": "ceilometer"
            },
            ],
        }}

        self.mock_response = mock.Mock()
        self.mock_response.json.return_value = response

        mock_post.return_value = self.mock_response

        client = ClientV2("test_auth_url", "test_username",
                          "test_password", "test_tenant")
        client.refresh()

        with self.assertRaises(MissingServices):
            client.get_service_endpoint('ceilometer')

    @mock.patch('collectd_ceilometer.keystone_light.requests.post')
    def test_invalidresponse_missing_access(self, mock_post):
        """Test invalid response: missing access"""

        response = {'badresponse': None}

        mock_response = mock.Mock()
        mock_response.json.return_value = response
        mock_post.return_value = mock_response

        client = keystone_light.ClientV2("test_auth_url", "test_username",
                                         "test_password", "test_tenant")

        with self.assertRaises(keystone_light.InvalidResponse):
            client.refresh()

    @mock.patch('collectd_ceilometer.keystone_light.requests.post')
    def test_invalidresponse_missing_servicecatalog(self, mock_post):
        """Test invalid response: missing servicecatalog"""

        response = {'access': {
            'token': None
            }
        }

        mock_response = mock.Mock()
        mock_response.json.return_value = response
        mock_post.return_value = mock_response

        client = keystone_light.ClientV2("test_auth_url", "test_username",
                                         "test_password", "test_tenant")

        with self.assertRaises(keystone_light.InvalidResponse):
            client.refresh()

    @mock.patch('collectd_ceilometer.keystone_light.requests.post')
    def test_invalidresponse_missing_token(self, mock_post):
        """Test invalid response: missing token"""

        response = {'access': {
            "serviceCatalog": []
        }}

        mock_response = mock.Mock()
        mock_response.json.return_value = response
        mock_post.return_value = mock_response

        client = keystone_light.ClientV2("test_auth_url", "test_username",
                                         "test_password", "test_tenant")

        with self.assertRaises(keystone_light.InvalidResponse):
            client.refresh()

    @mock.patch('collectd_ceilometer.keystone_light.requests.post')
    def test_invalidresponse_missing_id(self, mock_post):
        """Test  invalid response: missing id"""

        response = {'access': {
            "serviceCatalog": [],
            "token": None
        }, }

        mock_response = mock.Mock()
        mock_response.json.return_value = response
        mock_post.return_value = mock_response

        client = keystone_light.ClientV2("test_auth_url", "test_username",
                                         "test_password", "test_tenant")

        with self.assertRaises(keystone_light.InvalidResponse):
            client.refresh()

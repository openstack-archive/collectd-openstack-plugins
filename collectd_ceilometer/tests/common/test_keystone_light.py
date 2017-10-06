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

from collectd_ceilometer.common import keystone_light
from collectd_ceilometer.common.keystone_light import ClientV3
from collectd_ceilometer.common.keystone_light import MissingServices
import mock
import unittest


class KeystoneLightTestV3(unittest.TestCase):
    """Test the keystone light client with 3.0 keystone api"""

    def setUp(self):
        super(KeystoneLightTestV3, self).setUp()

        self.test_authtoken = "c5bbb1c9a27e470fb482de2a718e08c2"
        self.test_public_endpoint = "http://public_endpoint"
        self.test_internal_endpoint = "http://internal_endpoint"
        self.test_region = "RegionOne"

        response = {"token": {
            "is_domain": 'false',
            "methods": [
                "password"
            ],
            "roles": [
                {
                    "id": "eacf519eb1264cba9ad645355ce1f6ec",
                    "name": "ResellerAdmin"
                },
                {
                    "id": "63e481b5d5f545ecb8947072ff34f10d",
                    "name": "admin"
                }
            ],
            "is_admin_project": 'false',
            "project": {
                "domain": {
                    "id": "default",
                    "name": "Default"
                },
                "id": "97467f21efb2493c92481429a04df7bd",
                "name": "service"
            },
            "catalog": [
                {
                    "endpoints": [
                        {
                            "url": self.test_public_endpoint + '/',
                            "interface": "public",
                            "region": self.test_region,
                            "region_id": self.test_region,
                            "id": "5e1d9a45d7d442ca8971a5112b2e89b5"
                        },
                        {
                            "url": "http://127.0.0.1:8777",
                            "interface": "admin",
                            "region": self.test_region,
                            "region_id": self.test_region,
                            "id": "5e8b536fde6049d381ee540c018905d1"
                        },
                        {
                            "url": self.test_internal_endpoint + '/',
                            "interface": "internal",
                            "region": self.test_region,
                            "region_id": self.test_region,
                            "id": "db90c733ddd9466696bc5aaec43b18d0"
                        }
                    ],
                    "type": "metrics",
                    "id": "f6c15a041d574bc190c70815a14ab851",
                    "name": "gnocchi"
                }
            ]
            }
        }

        self.mock_response = mock.Mock()
        self.mock_response.json.return_value = response
        self.mock_response.headers = {
            'X-Subject-Token': "c5bbb1c9a27e470fb482de2a718e08c2"
        }

    @mock.patch('collectd_ceilometer.common.keystone_light.requests.post')
    def test_refresh(self, mock_post):
        """Test refresh"""

        mock_post.return_value = self.mock_response

        client = ClientV3("test_auth_url", "test_username",
                          "test_password", "test_tenant")

        self.assertEqual(client.auth_token, self.test_authtoken)

        expected_args = {
            'headers': {'Accept': 'application/json'},
            'json': {
                'auth': {
                    "identity": {
                        "methods": ["password"],
                        "password": {
                            "user": {
                                "name": u'test_username',
                                "domain": {"id": "default"},
                                "password": u'test_password'
                            }
                        }
                    },
                    "scope": {
                        "project": {
                            "name": u'test_tenant',
                            "domain": {"id": "default"}
                        }
                    }
                }
            }
        }

        mock_post.assert_called_once_with(
            'test_auth_url/auth/tokens',
            json=expected_args['json'],
            headers=expected_args['headers'],
        )

    @mock.patch('collectd_ceilometer.common.keystone_light.requests.post')
    def test_get_service_endpoint(self, mock_post):
        """Test get_service_endpoint"""

        mock_post.return_value = self.mock_response

        client = ClientV3("test_auth_url", "test_username",
                          "test_password", "test_tenant")
        client.refresh()

        endpoint = client.get_service_endpoint('gnocchi')
        self.assertEqual(endpoint, self.test_internal_endpoint)

        endpoint = client.get_service_endpoint('gnocchi', 'publicURL')
        self.assertEqual(endpoint, self.test_public_endpoint)

        endpoint = client.get_service_endpoint('gnocchi', 'publicURL',
                                               self.test_region)
        self.assertEqual(endpoint, self.test_public_endpoint)

        with self.assertRaises(MissingServices):
            client.get_service_endpoint('badname')

    @mock.patch('collectd_ceilometer.common.keystone_light.requests.post')
    def test_get_service_endpoint_error(self, mock_post):
        """Test get service endpoint error"""

        response = {"token": {
            "is_domain": 'false',
            "methods": [
                "password"
            ],
            "roles": [
                {
                    "id": "eacf519eb1264cba9ad645355ce1f6ec",
                    "name": "ResellerAdmin"
                },
                {
                    "id": "63e481b5d5f545ecb8947072ff34f10d",
                    "name": "admin"
                }
            ],
            "is_admin_project": 'false',
            "project": {
                "domain": {
                    "id": "default",
                    "name": "Default"
                },
                "id": "97467f21efb2493c92481429a04df7bd",
                "name": "service"
            },
            "catalog": [
                {
                    "endpoints": [],
                    "type": "metrics",
                    "id": "f6c15a041d574bc190c70815a14ab851",
                    "name": "badname"
                }
            ]
            }
        }

        self.mock_response = mock.Mock()
        self.mock_response.json.return_value = response
        self.mock_response.headers = {
            'X-Subject-Token': "c5bbb1c9a27e470fb482de2a718e08c2"
        }
        mock_post.return_value = self.mock_response

        client = ClientV3("test_auth_url", "test_username",
                          "test_password", "test_tenant")
        client.refresh()

        with self.assertRaises(MissingServices):
            client.get_service_endpoint('gnocchi')

    @mock.patch('collectd_ceilometer.common.keystone_light.requests.post')
    def test_invalidresponse_missing_token(self, mock_post):
        """Test invalid response: missing access"""

        response = {'badresponse': None}

        mock_response = mock.Mock()
        mock_response.json.return_value = response
        mock_response.headers = {
            'X-Subject-Token': "c5bbb1c9a27e470fb482de2a718e08c2"
        }
        mock_post.return_value = mock_response

        client = keystone_light.ClientV3("test_auth_url", "test_username",
                                         "test_password", "test_tenant")

        with self.assertRaises(keystone_light.InvalidResponse):
            client.refresh()

    @mock.patch('collectd_ceilometer.common.keystone_light.requests.post')
    def test_invalidresponse_missing_catalog(self, mock_post):
        """Test invalid response: missing catalog"""

        response = {"token": {
            "is_domain": 'false',
            "methods": [
                "password"
            ],
            "roles": [
                {
                    "id": "eacf519eb1264cba9ad645355ce1f6ec",
                    "name": "ResellerAdmin"
                },
                {
                    "id": "63e481b5d5f545ecb8947072ff34f10d",
                    "name": "admin"
                }
            ],
            "is_admin_project": 'false',
            "project": {
                "domain": {
                    "id": "default",
                    "name": "Default"
                },
                "id": "97467f21efb2493c92481429a04df7bd",
                "name": "service"
            },
            }
        }

        mock_response = mock.Mock()
        mock_response.json.return_value = response
        mock_response.headers = {
            'X-Subject-Token': "c5bbb1c9a27e470fb482de2a718e08c2"
        }
        mock_post.return_value = mock_response

        client = keystone_light.ClientV3("test_auth_url", "test_username",
                                         "test_password", "test_tenant")

        with self.assertRaises(keystone_light.InvalidResponse):
            client.refresh()

    @mock.patch('collectd_ceilometer.common.keystone_light.requests.post')
    def test_invalid_response_missing_token_http_header(self, mock_post):
        """Test invalid response: missing token in header"""

        response = {"token": {
            "is_domain": 'false',
            "methods": [
                "password"
            ],
            "roles": [
                {
                    "id": "eacf519eb1264cba9ad645355ce1f6ec",
                    "name": "ResellerAdmin"
                },
                {
                    "id": "63e481b5d5f545ecb8947072ff34f10d",
                    "name": "admin"
                }
            ],
            "is_admin_project": 'false',
            "project": {
                "domain": {
                    "id": "default",
                    "name": "Default"
                },
                "id": "97467f21efb2493c92481429a04df7bd",
                "name": "service"
            },
            "catalog": [
                {
                    "endpoints": [
                        {
                            "url": self.test_public_endpoint + '/',
                            "interface": "public",
                            "region": self.test_region,
                            "region_id": self.test_region,
                            "id": "5e1d9a45d7d442ca8971a5112b2e89b5"
                        },
                        {
                            "url": "http://127.0.0.1:8777",
                            "interface": "admin",
                            "region": self.test_region,
                            "region_id": self.test_region,
                            "id": "5e8b536fde6049d381ee540c018905d1"
                        },
                        {
                            "url": self.test_internal_endpoint + '/',
                            "interface": "internal",
                            "region": self.test_region,
                            "region_id": self.test_region,
                            "id": "db90c733ddd9466696bc5aaec43b18d0"
                        }
                    ],
                    "type": "metrics",
                    "id": "f6c15a041d574bc190c70815a14ab851",
                    "name": "gnocchi"
                }
            ]
            }
        }

        mock_response = mock.Mock()
        mock_response.json.return_value = response
        mock_post.return_value = mock_response

        client = keystone_light.ClientV3("test_auth_url", "test_username",
                                         "test_password", "test_tenant")

        with self.assertRaises(keystone_light.InvalidResponse):
            client.refresh()

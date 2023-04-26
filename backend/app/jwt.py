#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file
# except in compliance with the License. A copy of the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under the License.

import json
import time
import urllib.request
import logging

from jose import jwk, jwt
from jose.utils import base64url_decode

logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)


region = "us-east-2"
userpool_id = "us-east-2_y3Mq2SZ54"
app_client_id = "1tpl86djh4g2uslurljii62sgd"
keys_url = "https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json".format(
    region, userpool_id
)
# instead of re-downloading the public keys every time
# we download them only on cold start
# https://aws.amazon.com/blogs/compute/container-reuse-in-lambda/
with urllib.request.urlopen(keys_url) as f:
    response = f.read()
keys = json.loads(response.decode("utf-8"))["keys"]


class JwtToken:
    def __init__(self, token: str):
        self.token = token
        self._claims, status = self._get_claims()
        self.status = status
        self.username = ""
        self.groups = []
        self.email = ""
        self.valid = bool(self._claims)
        if self._claims:
            self.username = self._claims["cognito:username"]
            self.groups = self._claims["cognito:groups"]
            self.email = self._claims["email"]
            #  {
            #      "at_hash": "XL_kz-zWzliPaOMP8kYwcQ",
            #      "sub": "0ed898ca-ef6d-4e8c-91a6-1b4f4a2a4b47",
            #      "cognito:groups": ["us-east-2_y3Mq2SZ54_Google"],
            #      "email_verified": False,
            #      "iss": "https://cognito-idp.us-east-2.amazonaws.com/us-east-2_y3Mq2SZ54",
            #      "cognito:username": "Google_117789969009555435433",
            #      "origin_jti": "4c638366-fa8f-478f-8136-cb1f5a4ce3da",
            #      "aud": "1tpl86djh4g2uslurljii62sgd",
            #      "identities": [
            #          {
            #              "userId": "117789969009555435433",
            #              "providerName": "Google",
            #              "providerType": "Google",
            #              "issuer": None,
            #              "primary": "true",
            #              "dateCreated": "1681929530991",
            #          }
            #      ],
            #      "token_use": "id",
            #      "auth_time": 1682119257,
            #      "exp": 1682443944,
            #      "iat": 1682440344,
            #      "jti": "9dfd2370-d9f7-4943-8166-e6fd133f894d",
            #      "email": "hollingsworth.stevend@gmail.com",
            #  }

    def to_dict(self):
        return {
            "username": self.username,
            "groups": self.groups,
            "email": self.email,
            "valid": self.valid,
            "status": self.status,
        }

    def _get_claims(self):
        # get the kid from the headers prior to verification
        headers = jwt.get_unverified_headers(self.token)
        kid = headers["kid"]
        # search for the kid in the downloaded public keys
        key_index = -1
        for i in range(len(keys)):
            if kid == keys[i]["kid"]:
                key_index = i
                break
        if key_index == -1:
            return {}, "Public key not found in jwks.json"
        # construct the public key
        public_key = jwk.construct(keys[key_index])
        # get the last two sections of the token,
        # message and signature (encoded in base64)
        message, encoded_signature = str(self.token).rsplit(".", 1)
        # decode the signature
        decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))
        # verify the signature
        if not public_key.verify(message.encode("utf8"), decoded_signature):
            return {}, "Signature verification failed"
        logger.info("Signature successfully verified")
        # since we passed the verification, we can now safely
        # use the unverified claims
        claims = jwt.get_unverified_claims(self.token)
        # additionally we can verify the token expiration
        if time.time() > claims["exp"]:
            return {}, "Token is expired"
        # and the Audience  (use claims['client_id'] if verifying an access token)
        if claims["aud"] != app_client_id:
            return {}, "Token was not issued for this audience"
        # now we can use the claims
        return claims, "OK"
